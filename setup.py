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
            "markupsafe",  # newer version not compatible
            "pytest",
            "pytest-cov[toml]",
            "sqlalchemy~=1.3.0",
            "sqlalchemy-utils>=0.32,<0.36.4",
            "indexd @ git+ssh://git@github.com/NCI-GDC/indexd.git@2.11.1-rc.3#egg=indexd",
        ],
        "pytest_indexd": [
            "deepdiff<5.8",  # for python3.6
            "dataclasses; python_version < '3.7'",
            "importlib_resources; python_version < '3.7'",
            "psycopg",
            "pytest<7",
            "pytest-cov[toml]",
            "pytest-postgresql",
            "pytest-xdist",
            "pyyaml",
            "indexd @ git+ssh://git@github.com/NCI-GDC/indexd.git@2.11.1-rc.3#egg=indexd",
            "indexdmodels @ git+ssh://git@github.com/NCI-GDC/indexdmodels.git@0.2.0#egg=indexdmodels",
        ],
    },
)
