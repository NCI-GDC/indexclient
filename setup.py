from setuptools import find_packages, setup

setup(
    name="indexclient",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "requests~=2.5",
    ],
    extras_require={
        "dev": [
            "cdislogging==1.0.0",
            "markupsafe~=1.1.1",  # newer version not compatible
            "pre-commit~=1.21.0",
            "pytest~=6.2.0",
            "sqlalchemy~=1.3.0",
            "sqlalchemy-utils>=0.32,<0.36.4",
            "indexd @ git+https://github.com/NCI-GDC/indexd.git@2.9.0-rc.2#egg=indexd",
        ],
        "test_utils2": [
            "psycopg",
            "pytest~=6.2.0",
            "pytest-parallel",
            "pytest-postgresql",
            "pytest-xdist",
            "indexd @ git+https://github.com/NCI-GDC/indexd.git@2.9.0-rc.2#egg=indexd",
        ],
    },
)
