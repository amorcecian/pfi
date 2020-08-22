from os import getenv

config_data = {}

if getenv('APP_ENV') == 'local':
    config_data['DEBUG'] = True
else:
    config_data['DEBUG'] = False

config_data['API_TOKEN'] = getenv('API_TOKEN')
config_data['AUTHENTICATION_MODE'] = 'MasterUser'
config_data['SCOPE'] = ['https://analysis.windows.net/powerbi/api/.default']
config_data['AUTHORITY'] = 'https://login.microsoftonline.com/organizations'

if getenv('SERVER') is not None:
    config_data['SERVER'] = getenv('SERVER')
    config_data['USER'] = getenv('USER')
    config_data['PASSWORD'] = getenv('PASSWORD')
    config_data['DB'] = getenv('DB')
    config_data['WORKSPACE_ID'] = getenv('WORKSPACE_ID')
    config_data['REPORT_ID'] = getenv('REPORT_ID')
    config_data['CLIENT_ID'] = getenv('CLIENT_ID')
    config_data['POWER_BI_USER'] = getenv('POWER_BI_USER')
    config_data['POWER_BI_PASS'] = getenv('POWER_BI_PASS')

else:
    # Local DB PC
    config_data['SERVER'] = 'DESKTOP-3OHRULK'
    config_data['USER'] = 'sa'
    config_data['PASSWORD'] = 'welcome1'
    config_data['DB'] = 'pfidb'
