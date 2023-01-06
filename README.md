# Sample files to upload

## 环境

Tested with the following setup:

- python 2.7.18 with M1 Arm Chips
- a maximum of 500mb video files

## 依赖
```shell
pip install -r requirements.txt
```

## 配置
创建一个文件在~/.cos.ini
```ini
[default]
server_url = https://api.coscene.cn
project_slug = <WAREHOUSE/PROJECT>
api_key = <API_KEY>
```
替换上面带尖括号的里的内容

### 从地址栏获得slug
![find slug](img/slug.png)

### 从 coscene 网页右上角 点击头像 -> 设置 -> 安全 里生成一个对应的 apikey 使用
![token1](img/token1.png)
![token2](img/token2.png)
![token3](img/token3.png)

## Run
```shell
python cos.py -c ./sample.ini ./mocks/sample_data/2.jpg ./mocks/sample_data/3.jpg
python cos.py -c ./sample.ini --daemon --base-dir ./mocks/sample_data
```

## Swagger
Swagger 是 SmartBear 软件公司为 API 开发者提供的一套工具，也是 OpenAPI 规范所依据的一个规范。本地启动一个 server 提供获取 swagger.json 文件，为 ui 渲染做文件准备。

1. 启动本地 server，`python server.py` 
2. 浏览器打开网址 [swagger](https://petstore.swagger.io/)
3. 输入地址 `http://127.0.0.1:31338/swagger.json` 查看即可获取到接口文档

![swagger](img/swagger.png)
