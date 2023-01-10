import hashlib
import random
import uuid
from typing import Dict, Optional

from indexclient.client import Document, IndexClient
from indexclient.types import IndexData, IndexHash


def create_random_index(
    index_client: IndexClient,
    did: Optional[str] = None,
    version: Optional[str] = None,
    hashes: Optional[Dict[str, str]] = None,
) -> Document:
    """
    Shorthand for creating new index entries for test purposes.
    Note:
        Expects index client v1.5.2 and above
    Args:
        index_client (indexclient.client.IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): if specified it will be used as document did, else allows indexd to create one
        version (str): version of the index being added
        hashes (dict): hashes to store on the index, if not specified a random one is created
    Returns:
        indexclient.client.Document: the document just created
    """

    did = str(uuid.uuid4()) if did is None else did

    if not hashes:
        md5_hasher = hashlib.md5()
        md5_hasher.update(did.encode("utf-8"))
        hashes = {"md5": md5_hasher.hexdigest()}

    doc = index_client.create(
        did=did,
        hashes=hashes,
        size=random.randint(10, 1000),
        version=version,
        acl=["a", "b"],
        file_name=f"{did}_warning_huge_file.svs",
        urls=[f"s3://super-safe.com/{did}_warning_huge_file.svs"],
        urls_metadata={f"s3://super-safe.com/{did}_warning_huge_file.svs": {"a": "b"}},
    )

    return doc


def mock_doc(doc: IndexData) -> IndexData:
    """Adds fields needed by indexd create request to the input doc object"""

    # add dummy md5hash if no hash is specified
    if "hashes" not in doc:
        md5 = hashlib.md5()
        md5.update(doc["did"].encode("utf-8"))
        doc["hashes"] = IndexHash(md5=md5.hexdigest())
    if "size" not in doc:
        doc["size"] = random.randint(10, 1000)
    if "acl" not in doc:
        doc["acl"] = ["open"]
    if "urls_metadata" not in doc:
        doc["urls_metadata"] = {
            f"s3://ceph.service.consul/data-tools/{doc['did']}_test_file.svs": {
                "type": "cleversafe",
                "state": "validated",
            }
        }
    if "urls" not in doc:
        doc["urls"] = list(doc.get("urls_metadata", {}).keys())
    return doc


def create_random_index_version(
    index_client: IndexClient,
    did: str,
    version_did: Optional[str] = None,
    version: Optional[str] = None,
) -> Document:
    """
    Shorthand for creating a dummy version of an existing index, use wisely as it does not assume any versioning
    scheme and null versions are allowed
    Args:
        index_client (IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): existing member did
        version_did (str): did for the version to be created
        version (str): version number for the version to be created
    Returns:
        Document: the document just created
    """
    md5_hasher = hashlib.md5()
    md5_hasher.update(did.encode("utf-8"))
    file_name = did

    data = {}
    if version_did:
        data["did"] = version_did
        file_name = version_did
        md5_hasher.update(version_did.encode("utf-8"))

    data["acl"] = ["ax", "bx"]
    data["size"] = random.randint(10, 1000)
    data["hashes"] = {"md5": md5_hasher.hexdigest()}
    data["urls"] = [f"s3://super-safe.com/{file_name}_warning_huge_file.svs"]
    data["form"] = "object"
    data["file_name"] = f"{file_name}_warning_huge_file.svs"
    data["urls_metadata"] = {
        f"s3://super-safe.com/{file_name}_warning_huge_file.svs": {"a": "b"}
    }

    if version:
        data["version"] = version

    return index_client.add_version(did, Document(None, None, data))
