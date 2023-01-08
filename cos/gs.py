# -*- coding:utf-8 -*-
import json
import os
import signal
import sys
import time
import traceback

try:
    # noinspection PyCompatibility
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class GSDaemon:
    def __init__(self, api, base_dir):
        self.api = api
        self.base_dir = base_dir

        def signal_handler(sig, _):
            print("\nProgram exiting gracefully by {sig}".format(sig=sig))
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def _find_error_json(self):
        for root, _, files in os.walk(self.base_dir):
            for filename in files:
                if filename.endswith('.json'):
                    yield os.path.join(root, filename)

    def handle_error_json(self, error_json_path):
        with open(error_json_path, 'r') as fp:
            error_json = json.load(fp)

        # 如果 flag（文件已经找齐）为 True 并且还未 uploaded.
        if error_json['flag'] and "uploaded" not in error_json:
            print("==> Find an error json {error_json_path}".format(
                error_json_path=error_json_path
            ))
            error_dir, _ = error_json_path.rsplit('.', 1)
            error_tar = error_dir + ".log"

            if os.path.exists(error_tar):
                # 上传压缩打包的数据
                files = [error_tar]

            elif os.path.exists(error_dir):
                # 上传目录下所有数据
                files = [
                    os.path.join(root, filename)
                    for root, _, files in os.walk(error_dir)
                    for filename in files
                ]

            else:
                print("==> Neither {error_dir} nor {error_tar} exists.".format(
                    error_dir=error_dir,
                    error_tar=error_tar
                ))
                return

            print("==> Files to upload: \n\t{files}".format(
                files="\n\t".join(files)
            ))
            self.api.create_record_and_upload_files(os.path.basename(error_dir), files)

        # 把上传状态写回json
        error_json['uploaded'] = True
        with open(error_json_path, 'w') as fp:
            json.dump(error_json, fp, indent=4)

    def run(self):
        while True:
            print("==> Search for new error json")
            for error_json_path in self._find_error_json():
                # noinspection PyBroadException
                try:
                    self.handle_error_json(error_json_path)
                except Exception as _:
                    # 打印错误，但保证循环不被打断
                    traceback.print_exc()

            time.sleep(60)
