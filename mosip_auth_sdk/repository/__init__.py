from datetime import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()

class ExtendedBase:

    def add_to_session(self, session : Session):
        session.add(self)
        return self
    
    def add(self, engine):
        with Session(engine) as session:
            self.add_to_session(session)
            session.commit()
        return self
    
    def update_timestamp(self):
        self.upd_dtimes = datetime.utcnow()
    
    def update_commit_timestamp(self, session : Session = None):
        self.update_timestamp()
        if session:
            session.commit()
        return self

from .authtoken_request_data_repository import AuthTokenRequestDataRepository
from .authtoken_request_repository import AuthTokenRequestRepository