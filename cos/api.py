# -*- coding:utf-8 -*-
import hashlib

import requests
import six as six
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from cos.exception import CosException

try:
    # noinspection PyCompatibility
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class ApiClient:
    def __init__(self, api_base, api_key, project_full_slug):
        """
        :rtype: 返回的将是可以即时调用的ApiClient
        """
        self.api_base = api_base
        self.basic_auth = HTTPBasicAuth('apikey', api_key)
        self.request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.req_session = requests.Session()
        # noinspection PyTypeChecker
        retries = Retry(total=None,
                        backoff_factor=1,
                        status_forcelist=[500, 501, 502, 503, 504])
        self.req_session.mount('https://', HTTPAdapter(max_retries=retries))

        # 你可以分开输入 <warehouse_uuid> and <project_uuid>
        # 你也可以输入项目的slug（代币的意思）<warehouse_slug>/project_slug>, 例如 default/data_project
        # 以下代码会查询服务器，取得对应的 uuid,
        # 最终API调用的是project name，正则名，将会是 warehouses/<warehouse_uuid>/projects/<project_uuid>
        # 例如 warehouses/7ab79a38-49fb-4411-8f1b-dff4ae95b0e5/projects/8793e727-5ed9-4403-98a3-58906a975e55
        self.project_name = self.project_slug_to_name(project_full_slug)

    def create_record(self, file_infos, title="Default Test Name", description=""):
        """
        :param file_infos: 文件信息，是用make_file_info函数生成
        :param title: 记录的现实title
        :param description: 记录的描述
        :return: 创建的新记录，以json形式呈现
        """
        url = "{api_base}/dataplatform/v1alpha2/{parent}/records".format(
            api_base=self.api_base,
            parent=self.project_name
        )
        payload = {
            "title": title,
            "description": description,
            "head": {"files": file_infos}
        }

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.request_headers,
                auth=self.basic_auth
            )
            if response.status_code == 401:
                raise CosException("Unauthorized")

            result = response.json()
            print("==> Successfully created the record " + result.get("name"))
            return result

        except RequestException as e:
            six.raise_from(CosException('Create Record failed'), e)

    def _convert_project_slug(self, warehouse_id, proj_slug):
        """
        :param warehouse_id: 数据仓库的uuid
        :param proj_slug: 项目的单个slug，例如 data_project（不带warehouse部份）
        :return: 项目的正则名
        """
        name_mixin_slug = "warehouses/{warehouse_id}/projects/{proj_slug}".format(
            warehouse_id=warehouse_id,
            proj_slug=proj_slug
        )
        url = "{api_base}/dataplatform/v1alpha1/{name}:convertProjectSlug".format(
            api_base=self.api_base,
            name=name_mixin_slug
        )

        try:
            response = requests.post(
                url=url,
                json={"project": name_mixin_slug},
                headers=self.request_headers,
                auth=self.basic_auth
            )
            if response.status_code == 401:
                raise CosException("Unauthorized")

            result = response.json()
            print("==> The project name for {slug} is {name}".format(
                slug=proj_slug,
                name=result.get("project")
            ))
            return result.get('project')

        except RequestException as e:
            six.raise_from(CosException('Convert Project Slug failed'), e)

    def _convert_warehouse_slug(self, wh_slug):
        """
        :param wh_slug: 数仓的slug
        :return: 数仓的正则名
        """
        name_mixin_slug = "warehouses/" + wh_slug
        url = "{api_base}/dataplatform/v1alpha1/{name}:convertWarehouseSlug".format(
            api_base=self.api_base,
            name=name_mixin_slug,
        )

        try:
            response = requests.post(
                url=url,
                json={"warehouse": name_mixin_slug},
                headers=self.request_headers,
                auth=self.basic_auth
            )
            if response.status_code == 401:
                raise CosException("Unauthorized")

            result = response.json()
            print("==> The warehouse name for {slug} is {name}".format(
                slug=wh_slug,
                name=result.get("warehouse")
            ))
            return result.get('warehouse')

        except RequestException as e:
            six.raise_from(CosException('Convert Warehouse Slug failed'), e)

    def project_slug_to_name(self, project_full_slug):
        """
        :param: project_full_slug: 项目的slug（代币的意思）<warehouse_slug>/project_slug>, 例如 default/data_project
        :return: 项目的正则名，例如
            warehouses/7ab79a38-49fb-4411-8f1b-dff4ae95b0e5/projects/8793e727-5ed9-4403-98a3-58906a975e55
        """
        wh_slug, proj_slug = project_full_slug.split('/')
        warehouse_id = self._convert_warehouse_slug(wh_slug).split('/')[1]
        project_id = self._convert_project_slug(warehouse_id, proj_slug).split('/')[3]
        return "warehouses/{warehouse_id}/projects/{project_id}".format(
            warehouse_id=warehouse_id,
            project_id=project_id
        )

    @staticmethod
    def _make_file_info(filepath):
        """
        :param filepath: 文件路径
        :return: 最终文件名，sha256，大小以及输入的路径组成的json
        """
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

            return {
                "filename": Path(filepath).name,
                "sha256": sha256_hash.hexdigest(),
                "size": Path(filepath).stat().st_size,
                "filepath": filepath
            }

    @staticmethod
    def _make_file_resource_name(record, file_info):
        return "{record_name}/files/{filename}".format(
            record_name=record.get("name"),
            filename=file_info.get("filename")
        )

    def generate_upload_urls(self, record, file_infos):
        """
        :param record: 记录json
        :param file_infos: 需要生成记录的文档
        :return:
        """
        url = "{api_base}/dataplatform/v1alpha2/{record_name}:generateUploadUrls".format(
            api_base=self.api_base,
            record_name=record.get("name")
        )
        payload = {"files": file_infos}

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.request_headers,
                auth=self.basic_auth
            )

            upload_urls = response.json()
            print("==> Successfully requested upload urls")
            return upload_urls.get("preSignedUrls")

        except RequestException as e:
            six.raise_from(CosException('Request upload urls failed'), e)

    def upload_file(self, filepath, upload_url):
        """
        :param filepath: 需要上传文件的本地路径
        :param upload_url: 上传用的预签名url
        """
        print("==> Start uploading " + filepath)

        # 使用tqdm实现进度条，disable=None的时候在非tty环境不显示进度
        with tqdm(
                total=Path(filepath).stat().st_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                disable=None
        ) as t, open(filepath, "rb") as f:
            wrapped_file = CallbackIOWrapper(t.update, f, "read")
            response = self.req_session.put(upload_url, data=wrapped_file)
            response.raise_for_status()

        print("==> Finished uploading " + filepath)

    def create_record_and_upload_files(self, title, filepaths):
        """
        :param title: 记录的标题
        :param filepaths: 需要上传的本地文件清单
        """
        print("==> Start creating records for Project " + self.project_name)

        # 1. 计算sha256，生成文件清单
        file_infos = [self._make_file_info(path) for path in filepaths]

        # 2. 为即将上传的文件创建记录
        record = self.create_record(file_infos, title)

        # 3. 为拿到的 Blobs 获取上传链接，已存在的Blob将被过滤
        upload_urls = self.generate_upload_urls(record, file_infos)

        # 4. 上传文件
        for f in file_infos:
            key = self._make_file_resource_name(record, f)
            if key in upload_urls:
                self.upload_file(f.get('filepath'), upload_urls.get(key))

        print("==> Done")
