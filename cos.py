# -*- coding:utf-8 -*-
import hashlib
import json
import os
import itertools

import requests


def get_authorized_headers(BEARER_TOKEN):
    return {
        "Authorization": "Bearer " + BEARER_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def default_params(page_size="10"):
    return {"page_size": page_size}


def create_record(
        API_BASE,
        WAREHOUSE_ID,
        PROJECT_ID,
        authorized_headers,
        name="Default Test Name",
):
    payload = {"title": name}

    try:
        response = requests.post(
            url=API_BASE + "/dataplatform/v1alpha2/warehouses/" +
                WAREHOUSE_ID + "/projects/" + PROJECT_ID + "/records",
            json=payload,
            headers=authorized_headers,
        )
        if response.status_code == 401:
            raise Exception("Unauthorized")

        result = response.json()

        print("Successfully created the record " + result.get("name"))
        return result

    except requests.exceptions.RequestException:
        raise Exception("Create Record failed")


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


def generate_new_revision_for_record_with_files(API_BASE, record, filepaths,
                                                authorized_headers):
    # Generte file lists, including
    # filename, size, and sha256
    files = generate_file_list_from_filepaths(filepaths)

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

    try:
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=authorized_headers,
        )

        revision = response.json()
        print("Successfully generated a new revision")
        return revision

    except requests.exceptions.RequestException as e:
        print("Generarte Revision failed")
        print(e)


def get_blobs_for_revision_files(API_BASE, record, revision_files, authorized_headers):
    # Generte file lists, including
    # filename, size, and sha256
    url = API_BASE + "/dataplatform/v1alpha2/" + record.get(
        "name") + "/blobs:batchGet"

    revision_filenames = [
        record.get("name") + "/blobs/" + revision_file.get("sha256")
        for revision_file in revision_files
    ]

    payload = {"requests.name": ",".join(revision_filenames)}

    try:
        response = requests.get(
            url=url,
            params=payload,
            headers=authorized_headers,
        )

        blobs = response.json()
        print("Successfully get blobs")
        return blobs

    except requests.exceptions.RequestException as e:
        print("Getting blobs failed")
        print(e)


def request_upload_urls_for_blobs(API_BASE, record, blobs, authorized_headers):
    # Generte file lists, including
    # filename, size, and sha256

    url = API_BASE + "/dataplatform/v1alpha2/" + record.get(
        "name") + ":batchGenerateUploadUrls"

    blob_names = map(lambda blob: {"blob": blob.get("name")},
                     blobs.get("blobs"))

    payload = {"requests": list(blob_names)}

    try:
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=authorized_headers,
        )

        upload_urls = response.json()
        print("Successfully requested upload urls")
        return upload_urls

    except requests.exceptions.RequestException as e:
        print("Request upload urls failed")
        print(e)


def find_blob_name_for_file(filepath, revision_files, blobs):
    filename = os.path.basename(filepath)

    revision_file = next(
        itertools.ifilter(lambda rf: rf.get("filename") == filename,
                          revision_files), None)
    blob = next(
        itertools.ifilter(
            lambda blob: blob.get("sha256") == revision_file.get("sha256"),
            blobs.get("blobs")), None)

    if blob.get("state").get("phase") == "ACTIVE":
        print("Skipping as this blob already exists")
        return None
    else:
        return blob.get("name")


def upload_files(filepaths, revision_files, blobs, upload_urls):
    for i in range(len(filepaths)):
        blob_name = find_blob_name_for_file(filepaths[0], revision_files,
                                            blobs)
        if blob_name is None:
            return

        upload_url = upload_urls.get("preSignedUrls", {}).get(blob_name, None)
        if upload_url is not None:
            with open(filepaths[i], 'rb') as f:
                print("Start uploading " + filepaths[i])
                response = requests.put(upload_url, data=f)
                response.raise_for_status()
                print("Finished uploading " + filepaths[i])


def create_record_and_upload_files(API_BASE, BEARER_TOKEN, WAREHOUSE_ID, PROJECT_ID,
                                   record_name, filepaths):
    # 1. 获取您的 BEARER Token, Warehouse ID 和 Project ID
    print("Start creating records for Projects " + PROJECT_ID)

    authorized_headers = get_authorized_headers(BEARER_TOKEN)

    # 2. 为即将上传的文件创建记录
    record = create_record(API_BASE, WAREHOUSE_ID, PROJECT_ID, authorized_headers,
                           record_name)

    # 3. 在刚创建的记录上，声明文件清单，创建一个新的版本
    # TODO, this only works for one file, still figuring out how to do multiple file batch get blob
    revision = generate_new_revision_for_record_with_files(
        API_BASE, record, filepaths, authorized_headers)

    # 4. 从新建的版本中获取文件信息，找到这些文件的 Blob 信息
    revision_files = list(
        filter(lambda file: file.get("filename") != ".cos/config.json",
               revision.get("files")))

    blobs = get_blobs_for_revision_files(API_BASE, record, revision_files,
                                         authorized_headers)

    # 5. 为拿到的 Blobs 获取上传链接，进行上传

    upload_urls = request_upload_urls_for_blobs(API_BASE, record, blobs,
                                                authorized_headers)

    # 6. 上传文件

    upload_files(filepaths, revision_files, blobs, upload_urls)

    print("Done")
