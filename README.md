# Sample files to upload

## Environment

Tested with the following setup:

- python 2.7.18 with M1 Arm Chips
- a maximum of 500mb video files

## Dependency

- requests

## Setup

Replace these info in the beginning of the file:

- bearer token
- project_slug

## Run
```shell
python cos.py --bearer-token <YOUR_BEARER_TOKEN> ./samples/2.jpg ./samples/3.jpg
```
