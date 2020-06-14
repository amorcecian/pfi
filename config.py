from os import getenv


if getenv('SERVER') is not None:
    SERVER = getenv('SERVER')
    USER = getenv('USER')
    PASSWORD = getenv('PASSWORD')
    DB = getenv('DB')
else:
    # Local DB PC
    SERVER = 'DESKTOP-3OHRULK'
    USER = 'sa'
    PASSWORD = 'welcome1'
    DB = 'pfidb'