from setuptools import setup, find_packages


setup(
    name='coSentinel',
    version='0.1',
    author='Yangming Huang',
    description='A tiny agent to send data to coScene data platform',
    url='https://github.com/coscene-io/sample-json-api-files',
    keywords='data, agent, upload, daemon',
    python_requires='>=2.7, <3',
    packages=find_packages(include=['cos']),
    install_requires=[
        'certifi==2021.10.8',
        'pathlib2~=2.3.7.post1',
        'requests~=2.27.1',
        'six~=1.16.0',
        'tqdm~=4.64.1',
        'setuptools~=44.1.1'
    ],
    entry_points={
        'console_scripts': [
            'cos=cos:main',
        ]
    }
)
