# -*- coding:utf-8 -*-
import hashlib
import json
import os

import requests

# BASE INFO
API_BASE = "https://api.coscene.dev"

# Account Specific
BEARER_TOKEN = "eyJraWQiOiI2YmE0N2Y0My02MWZkLTRlOGYtODhjMy05MTZjZTU3YjZlY2IiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhYmQ4OTBmMC1iMDViLTQwZjktOTllOC02YzFkMjI4ZmU4M2MiLCJpc3MiOiJodHRwczovL2FwaS5jb3NjZW5lLmRldi9zdXBlcnRva2Vucy1zZXJ2ZXIvYXV0aCIsImV4cCI6MTY2ODI3NzE3NywiaWF0IjoxNjY4MjU1NTQ2LCJvcmdJZCI6IjNmZjkxOGM3LTVkOGQtNDA0Yy1iZWJiLWU1NDk4NTI3ZDg5NSJ9.IylTi3XHxmFEp3XyoPXuS0Sm54eV1pZqcYgSTfzfQJrqBdC4ZFQULgffOegI8ruy_zEMdfW-NDvM7d6HrRZBmeWQp68whSHW4MD4VZr3KYMi73Lvu8RAgfo8TUfdGH2Z6jq6y2I4LaryQBfRBCrApVTvVPAlyEonL4OmteGNu9knxT17GYN4P3SC7TTq3Nf-NnvDYt_oa7qfO06MyvRlmgFu98uc10Ew26O1AZDMY0sb3k7orkR3L6-qoKo7QUWNiSrKLzACmZlMptw8Dkob8EY202G0es571x70NaF2sgSz-3MZ_DWAJM--gtUReWLl6eUi4FblKxS5FuCFeldY7Q"
WAREHOUSE_ID = "1c593c01-eaa3-4b85-82ed-277494820866"
PROJECT_ID = "2b329c23-2d16-4290-a586-c7ad63b6f1d1"


def authorized_headers():
    return {"Authorization": "Bearer " + BEARER_TOKEN}


def default_params(page_size="10"):
    return {"page_size": page_size}


def create_record(name="Default Test Name"):

    try:
        response = requests.post(
            url=API_BASE + "/dataplatform/v1alpha2/warehouses/" +
            WAREHOUSE_ID + "/projects/" + PROJECT_ID + "/records",
            data=json.dumps({"title": name}),
            headers=authorized_headers(),
        )
        # parse result to json
        result = response.json()
        print("Successfully created the record")
        return result

    except requests.exceptions.RequestException:
        print("Create Record failed")


def generate_file_list_from_filepaths(filepaths):
    files = []
    sha256_hash = hashlib.sha256()
    for i in range(len(filepaths)):
        with open(filepaths[i], "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

            files.append({
                "name": "",
                "filename": os.path.basename(filepaths[0]),
                "sha256": sha256_hash.hexdigest(),
                "size": os.path.getsize(filepaths[0]),
                "mediaType": ""
            })
    return files


def generate_new_revision_for_record_with_files(record, filepaths):
    # Generte file lists, including
    # filename, size, and sha256
    files_list = generate_file_list_from_filepaths(filepaths)

    url = API_BASE + "/dataplatform/v1alpha2/" + record.get(
        "name") + "/revisions:generate"

    payload = {
        "parent": record.get("name"),
        "revision": {
            "name": "",
            "description": "",
            "sha256": "",
            "parentSha256": "",
            "filesList": files_list,
            "transformationsList": [],
        },
        "method": 2
    }

    print(json.dumps(payload))

    try:
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=authorized_headers(),
        )

        revision = response.json()
        print("Successfully generated a new revision")
        return revision

    except requests.exceptions.RequestException as e:
        print("Generarte Revision failed")
        print(e)


if __name__ == "__main__":
    print("Start creating records for Projects " + PROJECT_ID)

    # 1. 获取您的 Auth Token, Warehouse ID / Slug 和 Project ID / Slug

    # 2. 为即将上传的文件创建记录
    record = create_record(name="Test Record")

    # 3. 在刚创建的记录上，声明文件清单，创建一个新的版本
    sample_files = ["./nihon.jpg"]
    revision = generate_new_revision_for_record_with_files(
        record, sample_files)

    # 4. 对记录中的文件生成上传连接

    # 5. 上传文件
