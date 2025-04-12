import datetime
import uuid
from typing import Annotated

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func



def auto_repr(cls):
    def __repr__(self):
        columns = self.__table__.columns.keys()
        values = {col: getattr(self, col) for col in columns}
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r:.10}' for k, v in values.items())})"
    
    
    cls.__repr__ = __repr__
    return cls


def utcnow():
    return datetime.datetime.now(datetime.UTC)


def undashed_uuid() -> str:
    return uuid.uuid4().hex.upper()



intpk = Annotated[int, mapped_column(primary_key=True)]
strpk = Annotated[str, mapped_column(primary_key=True)]
uuidpk = Annotated[str, mapped_column(primary_key=True, default=undashed_uuid)]
created_col = Annotated[datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), sort_order=1000)]
modified_col = Annotated[datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=utcnow, sort_order=1001)]


class SerialPK_Mixin:
    id = mapped_column(Integer, sort_order=-1000, primary_key=True)


class UUIDPK_Mixin:
    uuid = mapped_column(String, primary_key=True, default=undashed_uuid, sort_order=-999)


class TimestampMixin:
    created: Mapped[created_col]
    modified: Mapped[modified_col]



