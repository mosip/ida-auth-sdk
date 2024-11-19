from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import Base, ExtendedBase

class AuthTokenRequestRepository(Base, ExtendedBase):
    __tablename__ = "auth_requests"
    id = Column(Integer, primary_key=True)
    auth_request_id = Column(String(36), nullable=False, unique=True, index=True)
    number_processed = Column(Integer, default=0)
    number_error = Column(Integer, default=0)
    number_total = Column(Integer, nullable=False)
    input_type = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False)
    status = Column(String)
    cr_dtimes = Column(DateTime, nullable=False, default=datetime.utcnow)
    upd_dtimes = Column(DateTime)

    @classmethod
    def get_from_session(cls, session : Session, req_id):
        stmt = select(cls).where(cls.auth_request_id==req_id)
        return session.scalars(stmt).one()
    
    @classmethod
    def fetch_status(cls, req_id, engine):
        status = None
        with Session(engine) as session:
            status = cls.get_from_session(session, req_id).status
        return status