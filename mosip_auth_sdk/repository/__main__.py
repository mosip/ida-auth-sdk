import os
import sys
from . import db_tools
from dynaconf import Dynaconf

from mosip_token_seeder import init_config

available_subcommands = ['dbinit']

config = init_config()

if len(sys.argv)<2 or sys.argv[1] not in available_subcommands:
    sys.exit('Available subcommands:\n\t%s' % '\n\t'.join(available_subcommands))
subcommand = sys.argv[1]
if subcommand == available_subcommands[0]:
    if len(sys.argv)>2:
        sys.exit('Usage:\n\tpython -m %s %s' % (__package__,subcommand))
    if config.db.get('generate_db_always',True):
        username = config.db.username
        password = config.db.password
        location = config.db.location
        if config.db.get('generate_password_always',True):
            password = db_tools.generate_password(config.db.random_password_length)
        eng = db_tools.db_init(location, username, password)
        db_tools.db_create(eng)
        print(password)
    else:
        print(config.db.password)