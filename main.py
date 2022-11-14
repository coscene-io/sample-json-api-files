# -*- coding:utf-8 -*-
import argparse

from cos import ApiClient


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
        "eyJraWQiOiI3ZTAwZWRjZC1mY2Q0LTQ5M2YtYmUxYy0yZWQ1ZDI0NWQxMDUiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwNWMwOWZjMC0wMzcxLTRiMGItYmRlOS02MWJhOWYwMWMwODIiLCJpc3MiOiJodHRwczovL2FwaS5jb3NjZW5lLmNuL3N1cGVydG9rZW5zLXNlcnZlci9hdXRoIiwiZXhwIjoxNjY4NDQyNTA3LCJpYXQiOjE2Njg0MjA4NzYsIm9yZ0lkIjoiNmI0ZDhjOTgtY2M2Ny00N2VhLTk2MjUtZTdiMjk1YzQ2YmI4In0.KOSELnF4gj57XmfN3ZFrTq6RyNfrjeIjITek-Q1JEAU9SC5_F0WchhYso3DFeAvvG9DNvnpfXykElkaT9Bs3JWjDo0_9vETCMePeLqyRT4a_4TByyvUVI7PQhygOump2KqZMTj48La6K8LS0V1BD7Abm-u1gm9goRuoR7YQ3Gr7hXAHYCXd4Vbo6sxXBt_ZC3JRm00O818B1Gq92rOKm9FAYhaYqqEvrwTwnPRsLZBtQHs6B1-xMUpgS560JgvMl6E45EJv9XQJOknPV2fC8dzbhKympBIqUoeu8ortxfbmsWuLCwOIe-67nG8pg1FBIqRqjII9yLIHdG83f2BbOKg",
        "./samples/3.jpg"
    ])
