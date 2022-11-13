# -*- coding:utf-8 -*-
import hashlib
import json
import os

import requests

# BASE INFO
API_BASE = "https://api.coscene.dev"

# Account Specific
BEARER_TOKEN = "eyJraWQiOiI2YmE0N2Y0My02MWZkLTRlOGYtODhjMy05MTZjZTU3YjZlY2IiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhYmQ4OTBmMC1iMDViLTQwZjktOTllOC02YzFkMjI4ZmU4M2MiLCJpc3MiOiJodHRwczovL2FwaS5jb3NjZW5lLmRldi9zdXBlcnRva2Vucy1zZXJ2ZXIvYXV0aCIsImV4cCI6MTY2ODMyNjk3NCwiaWF0IjoxNjY4MzA1MzQzLCJvcmdJZCI6IjNmZjkxOGM3LTVkOGQtNDA0Yy1iZWJiLWU1NDk4NTI3ZDg5NSJ9.R4te1MUKYkpM1GbEvPVI4Y8Yl3Z1920TTCNfqhBmMlmbN5yRHX2iOiXSVbhmJLILc3PcPa6qgIHtVSfBHN9JNZco0lGKSH6AbdkQ0eFZt9Ka2AK67VF4R2r32UXpOMtFRIOGYYxJY2uqBlWD9Xx-v5rdH7kUJevaatKfcfQlEkldxzbNtDKlUzXMEWsN2WeAAQiQatghzbLUu34YljnragHTeWOIQnNVQasq0rxZkSTLF_SqkfrtlZaTxF3ix4E_FiVyYphCi3AT6JPmICyzqMTBhDErPLB4AtmbuspB8a7_aHsm4xAPpKDo4PqxW8k0kRYyiHhqtlSL5yZDbsmCrw"
WAREHOUSE_ID = "1c593c01-eaa3-4b85-82ed-277494820866"
PROJECT_ID = "2b329c23-2d16-4290-a586-c7ad63b6f1d1"

# Testing Data
# yapf: disable
# revision = {"files": [{"size": "3037426", "mediaType": "", "sha256": "752d5cfe5559085a81bd7e2c9d823c17bcfb109a947e79f5e48717bc0a237cab", "name": "warehouses/1c593c01-eaa3-4b85-82ed-277494820866/projects/2b329c23-2d16-4290-a586-c7ad63b6f1d1/records/b49e2323-f9d7-4a8f-93f0-9d1bf03e19be/files/nihon.jpg", "filename": "nihon.jpg"}, {"updateTime": "2022-11-13T03:07:25.141700212Z", "name": "warehouses/1c593c01-eaa3-4b85-82ed-277494820866/projects/2b329c23-2d16-4290-a586-c7ad63b6f1d1/records/b49e2323-f9d7-4a8f-93f0-9d1bf03e19be/files/.cos/config.json", "media": {"topics": [], "@type": "type.googleapis.com/coscene.dataplatform.v1alpha1.common.ConfigMedia", "createTime": "2022-11-13T03:07:25.141700212Z"}, "mediaType": "application/vnd.coscene.record.config.v1alpha1+json", "filename": ".cos/config.json", "sha256": "a0b5e961aaaa933587705d1d79673aaf28b6b0ed363c7f1a9fb389bca1199137", "createTime": "2022-11-13T03:07:25.141700212Z", "size": "535"}], "name": "warehouses/1c593c01-eaa3-4b85-82ed-277494820866/projects/2b329c23-2d16-4290-a586-c7ad63b6f1d1/records/b49e2323-f9d7-4a8f-93f0-9d1bf03e19be/revisions/a887831416f69d2e4f847aa3c60f4fd68b6f24ab27fc6c99458db50f9564591e", "description": "new revision including 2 files and 0 transformations", "parentSha256": "8070be24c4b1fbd8797476bfdc8e46fa622737c92bb5fe3f9f387132f790655a", "user": {"updateTime": "2022-11-12T12:19:04.329Z", "name": "users/abd890f0-b05b-40f9-99e8-6c1d228fe83c", "countryCallingCode": "", "tags": {"unionId": "c8t90vr7v66EVF3oawVKqQiEiE", "thirdPartyCorpId": "ding467e38c049a28c36a1320dcb25e91351", "thirdPartyId": "DING_TALK"}, "createTime": "2022-08-25T07:57:25.241Z", "phoneNumber": "", "avatar": "https://static-legacy.dingtalk.com/media/lADPDgQ9z5reJxjNAijNAig_552_552.jpg", "nickname": "\u90d1\u5b87\u9756", "email": "c8t90vr7v66evf3oawvkqqieie@coscene.auth", "metadata": {"agreedAgreement": "true"}}, "sha256": "a887831416f69d2e4f847aa3c60f4fd68b6f24ab27fc6c99458db50f9564591e", "config": {"topics": [], "createTime": "2022-11-13T03:07:25.136978760Z"}, "createTime": "2022-11-13T03:07:25.136978760Z", "transformations": []}
# yapf: enable


def authorized_headers():
    return {
        "Authorization": "Bearer " + BEARER_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def default_params(page_size="10"):
    return {"page_size": page_size}


def create_record(name="Default Test Name"):

    payload = {"title": name}

    try:
        response = requests.post(
            url=API_BASE + "/dataplatform/v1alpha2/warehouses/" +
            WAREHOUSE_ID + "/projects/" + PROJECT_ID + "/records",
            json=payload,
            headers=authorized_headers(),
        )
        if response.status_code == 401:
            raise Exception("Unauthorized")
        # parse result to json
        result = response.json()

        print(response.status_code)
        print("Successfully created the record " + result.get("name"))
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
                "filename": os.path.basename(filepaths[i]),
                "sha256": sha256_hash.hexdigest(),
                "size": os.path.getsize(filepaths[i]),
                "mediaType": ""
            })
    return files


def generate_new_revision_for_record_with_files(record, filepaths):
    # Generte file lists, including
    # filename, size, and sha256
    files = generate_file_list_from_filepaths(filepaths)
    print(files)

    url = API_BASE + "/dataplatform/v1alpha2/" + record.get(
        "name") + "/revisions:generate"

    payload = {
        "revision": {
            "name": "",
            "sha256": "",
            "parentSha256": "",
            "description": "",
            "files": files,
            "transformationsList": [],
        }
    }
    print(payload)

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


def get_blobs_for_revision_files(record, revision_files):
    # Generte file lists, including
    # filename, size, and sha256
    url = API_BASE + "/dataplatform/v1alpha2/" + record.get(
        "name") + "/blobs:batchGet"

    revision_filenames = [
        record.get("name") + "/blobs/" + revision_file.get("sha256")
        for revision_file in revision_files
    ]

    payload = {"requests.name": ",".join(revision_filenames)}
    print(payload)

    try:
        response = requests.get(
            url=url,
            params=payload,
            headers=authorized_headers(),
        )

        blobs = response.json()
        print("Successfully get blobs")
        return blobs

    except requests.exceptions.RequestException as e:
        print("Getting blobs failed")
        print(e)


def request_upload_urls_for_blobs(record, blobs):
    print(record)
    print(blobs)


def upload_files(filepaths, upload_urls):
    print(filepaths)
    print(upload_urls)


if __name__ == "__main__":
    print("Start creating records for Projects " + PROJECT_ID)

    # 1. 获取您的 Auth Token, Warehouse ID / Slug 和 Project ID / Slug

    # 2. 为即将上传的文件创建记录
    record = create_record(name="Test Record")

    # 3. 在刚创建的记录上，声明文件清单，创建一个新的版本
    # TODO, this only works for one file, stilling figuring out how to do multiple file batch get blob
    # JSON mapping kinda vague here
    sample_files = ["./nihon.jpg"]
    revision = generate_new_revision_for_record_with_files(
        record, sample_files)

    # 4. 从新建的版本中获取文件信息，找到这些文件的 Blob 信息
    revision_files = filter(
        lambda file: file.get("filename") != ".cos/config.json",
        revision.get("files"))

    blobs = get_blobs_for_revision_files(record, list(revision_files))

    # 5. 为拿到的 Blobs 获取上传链接，进行上传

    upload_urls = request_upload_urls_for_blobs(record, blobs)

    # 6. 上传文件

    upload_files(sample_files, upload_urls)
