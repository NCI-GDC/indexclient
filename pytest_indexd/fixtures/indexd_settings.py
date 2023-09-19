import os

from indexd.alias.drivers.alchemy import SQLAlchemyAliasDriver
from indexd.auth.drivers.alchemy import SQLAlchemyAuthDriver
from indexd.index.drivers.alchemy import SQLAlchemyIndexDriver


def get_settings(pg_url):
    CONFIG = {}

    CONFIG["JSONIFY_PRETTYPRINT_REGULAR"] = False
    AUTO_MIGRATE = True
    SQLALCHEMY_VERBOSE = os.getenv("INDEXD_VERBOSE", "").lower() in ["1", "yes", "true"]

    CONFIG["INDEX"] = {
        "driver": SQLAlchemyIndexDriver(
            pg_url,
            auto_migrate=AUTO_MIGRATE,
            echo=SQLALCHEMY_VERBOSE,
            index_config={
                "DEFAULT_PREFIX": "testprefix:",
                "ADD_PREFIX_ALIAS": True,
                "PREPEND_PREFIX": True,
            },
        ),
    }

    CONFIG["ALIAS"] = {
        "driver": SQLAlchemyAliasDriver(
            pg_url, auto_migrate=AUTO_MIGRATE, echo=SQLALCHEMY_VERBOSE
        ),
    }

    CONFIG["DIST"] = [
        {
            "name": "Other IndexD",
            "host": "https://indexd.example.io/index/",
            "hints": [".*ROCKS.*"],
            "type": "indexd",
        },
        {
            "name": "DX DOI",
            "host": "https://doi.org/",
            "hints": [r"10\..*"],
            "type": "doi",
        },
        {
            "name": "DOS System",
            "host": "https://example.com/api/ga4gh/dos/v1/",
            "hints": [],
            "type": "dos",
        },
    ]

    AUTH = SQLAlchemyAuthDriver(pg_url)

    return {"config": CONFIG, "auth": AUTH}
