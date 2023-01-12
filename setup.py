from setuptools import find_packages, setup

setup(
    name="indexclient",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "requests~=2.5",
    ],
    entry_points={"pytest11": ["pytest_indexd = pytest_indexd.plugin"]},
    extras_require={
        "dev": [
            "cdislogging==1.0.0",
            "markupsafe~=1.1.1",  # newer version not compatible
            "pre-commit~=1.21.0",
            "pytest~=6.2.0",
            "sqlalchemy~=1.3.0",
            "sqlalchemy-utils>=0.32,<0.36.4",
            "indexd @ git+https://github.com/NCI-GDC/indexd.git@2.10.0-rc.0#egg=indexd",
        ],
        "pytest_indexd": [
            "psycopg",
            "pytest~=6.2.0",
            "pytest-parallel",
            "pytest-postgresql",
            "pytest-xdist",
            "indexd @ git+https://github.com/NCI-GDC/indexd.git@2.10.0-rc.0#egg=indexd",
        ],
    },
)
