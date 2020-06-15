from os import getenv

config_data = {}

if getenv('SERVER') is not None:
    config_data['SERVER'] = getenv('SERVER')
    config_data['USER'] = getenv('USER')
    config_data['PASSWORD'] = getenv('PASSWORD')
    config_data['DB'] = getenv('DB')
else:
    # Local DB PC
    config_data['SERVER'] = 'DESKTOP-3OHRULK'
    config_data['USER'] = 'sa'
    config_data['PASSWORD'] = 'welcome1'
    config_data['DB'] = 'pfidb'