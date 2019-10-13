import jsonschema
import uuid

from indexclient.mocks.errors import (
    NoRecordFound,
    UserError,
)
from indexclient.mocks.schema import POST_RECORD_SCHEMA


def create(client, data):
    try:
        jsonschema.validate(data, POST_RECORD_SCHEMA)
    except jsonschema.ValidationError as err:
        raise UserError(err)

    if not data.get('baseid'):
        data['baseid'] = str(uuid.uuid4())

    if not data.get('did'):
        data['did'] = str(uuid.uuid4())

    data['rev'] = str(uuid.uuid4())[:8]

    if client.store.get(data['did']):
        raise UserError('{did} already exists'.format(did=data['did']), 400)

    client.store[data['did']] = data

    return dict(
        did=data['did'],
        rev=data['rev'],
        baseid=data['baseid'],
    )


def get(client, did):
    record = client.store.get(did)
    if not record:
        raise NoRecordFound('no record found')
    return {
        'did': record.get('did'),
        'baseid': record.get('baseid'),
        'rev': record.get('rev'),
        'size': record.get('size'),
        'file_name': record.get('file_name'),
        'version': record.get('version'),
        'uploader': record.get('uploader'),
        'urls': record.get('urls'),
        'urls_metadata': record.get('urls_metadata'),
        'acl': record.get('acl'),
        'hashes': record.get('hashes'),
        'metadata': record.get('metadata'),
        'form': record.get('form'),
        'created_date': record.get('created_date'),
        "updated_date": record.get('updated_date'),
    }
