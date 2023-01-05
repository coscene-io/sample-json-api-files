# -*- coding:utf-8 -*-
import argparse
import hashlib
import json
import os
import signal
import sys
import time
import traceback
from ConfigParser import ConfigParser

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper


class CosException(Exception):
    pass


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

        self._req_sess = requests.Session()
        retries = Retry(total=None,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        self._req_sess.mount('https://', HTTPAdapter(max_retries=retries))

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
            print("Successfully created the record " + result.get("name"))
            return result

        except requests.exceptions.RequestException as e:
            raise CosException("Create Record failed"), None, sys.exc_info()[2]

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
            print("The project name for {slug} is {name}".format(
                slug=proj_slug,
                name=result.get("project")
            ))
            return result.get('project')

        except requests.exceptions.RequestException as e:
            raise CosException("Convert Project Slug failed"), None, sys.exc_info()[2]

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
            print("The warehouse name for {slug} is {name}".format(
                slug=wh_slug,
                name=result.get("warehouse")
            ))
            return result.get('warehouse')

        except requests.exceptions.RequestException as e:
            raise CosException("Convert Warehouse Slug failed"), None, sys.exc_info()[2]

    def project_slug_to_name(self, project_full_slug):
        """
        :param project_full_slug: 项目的slug（代币的意思）<warehouse_slug>/project_slug>, 例如 default/data_project
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
                "filename": os.path.basename(filepath),
                "sha256": sha256_hash.hexdigest(),
                "size": os.path.getsize(filepath),
                "filepath": filepath
            }

    @staticmethod
    def _make_blob_name(record, file_info):
        return "{record_name}/blobs/{sha256}".format(
            record_name=record.get("name"),
            sha256=file_info.get("sha256")
        )

    def get_blobs(self, record, blob_names):
        """
        :param record: 记录json
        :param blob_names: 获取的blob名字
        :return: 获取一列blob，包括他们的状态信息
        """
        url = "{api_base}/dataplatform/v1alpha2/{record_name}/blobs:customizedBatchGet".format(
            api_base=self.api_base,
            record_name=record.get("name")
        )

        try:
            response = requests.post(
                url=url,
                json={"blobs": blob_names},
                headers=self.request_headers,
                auth=self.basic_auth
            )

            print("Successfully get blobs")
            return response.json().get("blobs")

        except requests.exceptions.RequestException as e:
            raise CosException("Getting blobs failed"), None, sys.exc_info()[2]

    def generate_upload_urls(self, record, blobs):
        """
        :param record: 记录json
        :param blobs: 需要生成记录的文档
        :return:
        """
        url = "{api_base}/dataplatform/v1alpha2/{record_name}:batchGenerateUploadUrls".format(
            api_base=self.api_base,
            record_name=record.get("name")
        )
        payload = {
            "requests": [
                {
                    "blob": blob.get("name")
                }
                for blob in blobs
            ]
        }

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.request_headers,
                auth=self.basic_auth
            )

            upload_urls = response.json()
            print("Successfully requested upload urls")
            return upload_urls.get("preSignedUrls")

        except requests.exceptions.RequestException as e:
            raise CosException("Request upload urls failed"), None, sys.exc_info()[2]

    def upload_file_with_progress(self, filepath, upload_url):
        total_size = os.path.getsize(filepath)

        with open(filepath, "rb") as f:
            print("Start uploading " + filepath)
            with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                response = self._req_sess.put(upload_url, data=wrapped_file)
                response.raise_for_status()
            print("Finished uploading " + filepath)

    @staticmethod
    def upload_file(filepath, upload_url):
        """
        :param filepath: 需要上传文件的本地路径
        :param upload_url: 上传用的预签名url
        """
        with open(filepath, 'rb') as f:
            print("Start uploading " + filepath)
            response = requests.put(upload_url, data=f)
            response.raise_for_status()
            print("Finished uploading " + filepath)

    def create_record_and_upload_files(self, title, filepaths):
        """
        :param title: 记录的标题
        :param filepaths: 需要上传的本地文件清单
        """
        print("Start creating records for Project " + self.project_name)

        # 1. 计算sha256，生成文件清单
        file_infos = [self._make_file_info(path) for path in filepaths]

        # 2. 为即将上传的文件创建记录
        record = self.create_record(file_infos, title)

        # 3. 去掉已经上传过的文件
        blobs = self.get_blobs(record, [
            self._make_blob_name(record, f) for f in file_infos
        ])

        # 4. 为拿到的 Blobs 获取上传链接，已存在的Blob将被过滤
        upload_urls = self.generate_upload_urls(record, [
            blob for blob in blobs
            if blob.get("state").get("phase") != "ACTIVE"
        ])

        # 5. 上传文件
        for f in file_infos:
            blob_name = self._make_blob_name(record, f)
            if blob_name in upload_urls:
                self.upload_file_with_progress(f.get('filepath'), upload_urls.get(blob_name))

        print("Done")


class ConfigManager:
    def __init__(self, config_file, profile='default'):
        self.config_file = os.path.expanduser(config_file)
        self.profile = profile
        self.parser = ConfigParser()
        self.load()

    def get(self, key):
        return self.parser.has_option(self.profile, key) and self.parser.get(self.profile, key) or None

    def set(self, key, value):
        if not self.parser.has_section(self.profile):
            self.parser.add_section(self.profile)
        self.parser.set(self.profile, key, value)

    def load(self):
        self.parser.read(self.config_file)

    def save(self):
        with open(self.config_file) as f:
            self.parser.write(f)


class GSDaemon:
    def __init__(self, api, base_dir):
        self.api = api
        self.base_dir = base_dir

        def signal_handler(signal, frame):
            print("\nProgram exiting gracefully")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def _find_error_json(self):
        for root, _, files in os.walk(self.base_dir):
            for filename in files:
                if filename.endswith('.json'):
                    yield os.path.join(root, filename)

    def _upload_error_data(self, error_json_path):
        # FIXME：下面如果路径中还有其他点可能会出错
        error_dir, _ = error_json_path.split('.', 2)
        error_tar = error_dir + ".log"

        if os.path.exists(error_dir):
            # 上传目录下所有数据
            files = [
                os.path.join(root, filename)
                for root, _, files in os.walk(error_dir)
                for filename in files
            ]
        elif os.path.exists(error_tar):
            # 上传压缩打包的数据
            files = [error_tar]
        else:
            print("Neither %s nor %s exists." % (error_dir, error_tar))
            return

        print("Files to upload: %s" % files)
        self.api.create_record_and_upload_files(os.path.basename(error_dir), files)

    def handle_error_json(self, error_json_path):
        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)

        # 如果 flag（文件已经找齐）为 True 并且还未 uploaded.
        if error_json['flag'] and "uploaded" not in error_json:
            print("Find an error %s" % error_json_path)
            self._upload_error_data(error_json_path)

        # 把上传状态写回json
        error_json['uploaded'] = True
        with open(error_json_path, 'w') as fp:
            json.dump(error_json, fp, indent=4)

    def run(self):
        while True:
            print("Search for new error json")
            for error_json_path in self._find_error_json():
                # noinspection PyBroadException
                try:
                    self.handle_error_json(error_json_path)
                except Exception as _:
                    traceback.print_exc()
                finally:
                    pass

            time.sleep(60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', type=str)
    parser.add_argument('-p', '--project-slug', type=str)
    parser.add_argument('-t', '--title', type=str, default="Test Record")
    parser.add_argument('-d', '--description', type=str)
    parser.add_argument('--base-dir', type=str, default=".")
    parser.add_argument('--api-key', type=str)
    parser.add_argument('-c', '--config', type=str, default='~/.cos.ini')
    parser.add_argument('files', nargs='*', help='files or directory')
    parser.add_argument('--daemon', action="store_true")
    args = parser.parse_args()

    cm = ConfigManager(config_file=args.config)
    args.server_url = args.server_url or cm.get("server_url")
    args.api_key = args.api_key or cm.get("api_key")
    args.project_slug = args.project_slug or cm.get("project_slug")

    # 0. 初始化您的 API key, Warehouse ID 和 Project ID
    api = ApiClient(args.server_url, args.api_key, args.project_slug)

    if args.daemon:
        # do something in daemon
        GSDaemon(api, args.base_dir).run()
    else:
        api.create_record_and_upload_files(args.title, args.files)


if __name__ == "__main__":
    main()
