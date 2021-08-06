from setuptools import setup

setup(
    name='indexclient',
    version='2.0.0',
    packages=[
        'indexclient',
        'indexclient.parsers',
        'indexd_test_utils'
    ],
    install_requires=[
        'requests~=2.5',
    ],
)
