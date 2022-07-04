import sqlalchemy as sa
from sqlalchemy import orm


class IndexTransaction(object):
    def __init__(self, session_factory, read_only=True):
        self.session = session_factory()
        if read_only:
            self.session.execute("SET TRANSACTION READ ONLY")

    def __enter__(self):
        return self.session

    def __exit__(
        self,
        exc_type=None,
        exc_val=None,
        exc_tb=None,
    ) -> None:
        """Tries to commit amd close provided session. Rollback changes if an exception occurs"""
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()


class IndexDatabaseClient(object):
    def __init__(
        self, url, auto_commit=False, auto_flush=False, read_only=True, **kwargs
    ):
        self.read_only = read_only
        self.engine = sa.create_engine(url, **kwargs)
        self.session_factory = orm.sessionmaker(
            autocommit=auto_commit, autoflush=auto_flush, bind=self.engine
        )

    def transaction(self):
        return IndexTransaction(self.session_factory, self.read_only)
