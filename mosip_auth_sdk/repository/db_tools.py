import os
import string, secrets
from sqlalchemy import create_engine

from . import AuthTokenRequestDataRepository, AuthTokenRequestRepository

def db_init(datasource_location : str, username=None, password=None):
    loc = datasource_location
    if password:
        loc = loc.replace('<password>',password)
    if username:
        loc = loc.replace('<username>',username)
    eng = create_engine(datasource_location)
    return eng

def generate_password(random_password_length : int):
    return ''.join([secrets.choice(string.ascii_lowercase + string.digits) for _ in range(random_password_length)])

def db_create(eng):
    AuthTokenRequestRepository.metadata.create_all(eng)
    AuthTokenRequestDataRepository.metadata.create_all(eng)