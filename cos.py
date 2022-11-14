# -*- coding:utf-8 -*-
import argparse
import hashlib
import os

import requests


class ApiClient:
    def __init__(self, api_base, bearer_token, warehouse_id, project_id):
        self.api_base = api_base
        self.authorized_headers = {
            "Authorization": "Bearer " + bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.warehouse_id = warehouse_id
        self.project_id = project_id

    def create_record(self, file_infos, title="Default Test Name", description=""):
        url = "{api_base}/dataplatform/v1alpha2/warehouses/{warehouse}/projects/{project}/records".format(
            api_base=self.api_base,
            warehouse=self.warehouse_id,
            project=self.project_id
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
                headers=self.authorized_headers,
            )
            if response.status_code == 401:
                raise Exception("Unauthorized")

            result = response.json()
            print("Successfully created the record " + result.get("name"))
            return result

        except requests.exceptions.RequestException:
            raise Exception("Create Record failed")

    @staticmethod
    def make_file_info(filepath):
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
    def make_blob_name(record, file_info):
        return "{record_name}/blobs/{sha256}".format(
            record_name=record.get("name"),
            sha256=file_info.get("sha256")
        )

    def get_blobs(self, record, blob_names):
        url = "{api_base}/dataplatform/v1alpha2/{record_name}/blobs:customizedBatchGet".format(
            api_base=self.api_base,
            record_name=record.get("name")
        )

        try:
            response = requests.post(
                url=url,
                json={"blobs": blob_names},
                headers=self.authorized_headers,
            )

            print("Successfully get blobs")
            return response.json().get("blobs")

        except requests.exceptions.RequestException as e:
            print("Getting blobs failed")
            print(e)

    def generate_upload_urls(self, record, blobs):
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
                headers=self.authorized_headers,
            )

            upload_urls = response.json()
            print("Successfully requested upload urls")
            return upload_urls.get("preSignedUrls")

        except requests.exceptions.RequestException as e:
            print("Request upload urls failed")
            print(e)

    @staticmethod
    def upload_file(filepath, upload_url):
        with open(filepath, 'rb') as f:
            print("Start uploading " + filepath)
            response = requests.put(upload_url, data=f)
            response.raise_for_status()
            print("Finished uploading " + filepath)

    def create_record_and_upload_files(self, title, filepaths):
        print("Start creating records for Project " + self.project_id)

        # 1. 计算sha256，生成文件清单
        file_infos = [self.make_file_info(path) for path in filepaths]

        # 2. 为即将上传的文件创建记录
        record = self.create_record(file_infos, title)

        # 3. 去掉已经上传过的文件
        blobs = self.get_blobs(record, [
            self.make_blob_name(record, f) for f in file_infos
        ])

        # 4. 为拿到的 Blobs 获取上传链接，已存在的Blob将被过滤
        upload_urls = self.generate_upload_urls(record, [
            blob for blob in blobs
            if blob.get("state").get("phase") != "ACTIVE"
        ])

        # 5. 上传文件
        for f in file_infos:
            blob_name = self.make_blob_name(record, f)
            if blob_name in upload_urls:
                self.upload_file(f.get('filepath'), upload_urls.get(blob_name))

        print("Done")


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', type=str, default='https://api.coscene.cn')
    parser.add_argument('--warehouse', type=str, default='7ab79a38-49fb-4411-8f1b-dff4ae95b0e5')
    parser.add_argument('--project', type=str, default='8793e727-5ed9-4403-98a3-58906a975e55')
    parser.add_argument('--title', type=str, default="Test Record")
    parser.add_argument('--description', type=str)
    parser.add_argument('--base-dir', type=str, default=".")
    parser.add_argument('--bearer-token', type=str)
    parser.add_argument('files', nargs='*', help='files or directory')
    args = parser.parse_args(args)

    # 0. 初始化您的 BEARER Token, Warehouse ID 和 Project ID
    api = ApiClient(args.server_url, args.bearer_token, args.warehouse, args.project)
    api.create_record_and_upload_files(args.title, args.files)


if __name__ == "__main__":
    main([
        "--bearer-token",
        os.getenv("BEARER_TOKEN"),
        "./samples/2.jpg",
        "./samples/3.jpg",
        "./samples/nihon.jpg"
    ])
