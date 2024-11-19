from datetime import datetime
from sqlalchemy import Column, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from . import Base, ExtendedBase

class AuthTokenRequestDataRepository(Base,ExtendedBase):
    __tablename__ = "auth_request_data"
    __table_args__ = (
        UniqueConstraint('auth_request_id','auth_request_line_no'),
        Index('idx_req_id_index','auth_request_id','auth_request_line_no'),
    )
    id = Column(Integer, primary_key=True)
    auth_request_id = Column(String(36), nullable=False)
    auth_request_line_no = Column(Integer, nullable=False, default=0)
    auth_data_received = Column(String, nullable=False)
    auth_data_input = Column(String)
    auth_data_output = Column(String)
    token = Column(String)
    error_code = Column(String)
    error_message = Column(String)
    status = Column(String)
    cr_dtimes = Column(DateTime, nullable=False, default=datetime.utcnow)
    upd_dtimes = Column(DateTime)

    @classmethod
    def get_from_session(cls, session : Session, req_id, line_no):
        stmt = select(cls).where(and_(cls.auth_request_id==req_id,cls.auth_request_line_no==line_no))
        return session.scalars(stmt).one()

    @classmethod
    def get_all_from_session(cls, session : Session, req_id):
        stmt = select(cls).where(cls.auth_request_id==req_id)
        return session.scalars(stmt)
