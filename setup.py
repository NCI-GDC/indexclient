from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="indexclient",
    setup_requires=["setuptools_scm<7"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    use_scm_version={
        "local_scheme": "no-local-version",
        "write_to": "indexclient/_version.py",
    },
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
            "indexd",
        ],
        "pytest_indexd": [
            "deepdiff",
            "importlib_resources",
            "psycopg",
            "pytest",
            "pytest-cov[toml]",
            "pytest-postgresql",
            "pytest-xdist",
            "pyyaml",
            "indexd",
            "indexdmodels",
        ],
    },
)
