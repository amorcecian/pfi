from os import getenv

config_data = {}

if getenv('APP_ENV') == 'local':
    config_data['DEBUG'] = True
else:
    config_data['DEBUG'] = False

config_data['API_TOKEN'] = getenv('API_TOKEN')
if getenv('SERVER') is not None:
    config_data['SERVER'] = getenv('SERVER')
    config_data['USER'] = getenv('DB_USER')
    config_data['PASSWORD'] = getenv('PASSWORD')
    config_data['DB'] = getenv('DB')
    config_data['QUEUE'] = getenv('QUEUE')
else:
    # Local DB PC
    config_data['SERVER'] = 'DESKTOP-3OHRULK'
    config_data['USER'] = 'sa'
    config_data['PASSWORD'] = 'welcome1'
    config_data['DB'] = 'pfidb'
    config_data['QUEUE'] = 'data_bike'
