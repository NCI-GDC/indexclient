from types import TracebackType
from typing import Optional, Type, Any

from sqlalchemy import engine, orm

class IndexTransaction:
    session: orm.Session
    def __init__(self, session_factory: Type[orm.Session], read_only: bool) -> None: ...
    def __enter__(self) -> orm.Session: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[TracebackType] = None,
    ) -> None: ...

class IndexDatabaseClient:
    read_only: bool = True
    engine: engine.Engine
    session_factory: Type[orm.Session]
    def __init__(
        self,
        url: str,
        auto_commit: bool = False,
        auto_flush: bool = False,
        read_only: bool = True,
        **kwargs: Any
    ) -> None: ...
    def transaction(self) -> IndexTransaction: ...
