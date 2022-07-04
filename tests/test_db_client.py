from indexclient.sqlalchemy.models import IndexRecord


def test_init_dbclient(db_client):
    with db_client.transaction() as txn:
        records = txn.query(IndexRecord).count()
        print(records)
