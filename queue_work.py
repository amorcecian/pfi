import sqlalchemy
from sqlalchemy  import create_engine
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from config import config_data
# from computing_stations import *
from data_bike.computing_stations import engine_creation,group_stations,calculate_stations_usage,add_station
import os
import time

#######################################################
#Logger configuration
#######################################################
logstr = "%(asctime)s: %(levelname)s: Line:%(lineno)d %(message)s"
logging.basicConfig(#filename="output.log",
                    level=logging.INFO,
                    filemode="w",
                    format=logstr)


## Listening the queue file in order to activate a function
# __location__ = os.path.realpath(
#     os.path.join(os.getcwd(), os.path.dirname(__file__)))

data_folder = Path(config_data['QUEUE'])
file_to_open = data_folder / "queue"

# def clean_queue(status):
#     with open(os.path.join(__location__, 'queue'),'w') as f:
#         f.writelines(status[2:])

def clean_queue(status):
    with open(file_to_open,'w') as f:
        f.writelines(status[10:])

def clean_multiple_queue(status):
    with open(file_to_open,'w') as f:
        f.writelines(status[2:])

while True:
    # with open(os.path.join(__location__, 'queue'),'r') as f:
    with open(file_to_open,'r') as f:
        # data = f.readlines()
        status = f.read().split(',')
        logging.debug(status)
    if 'Pending' in status[0]:
        if 'Start' in status[1]:
            logging.info(f"Doing {status[1]}")
            engine = engine_creation()
            group_stations(engine)
            calculate_stations_usage(engine)
            clean_queue(status)
            logging.info(f"{status[1]} finished")
        elif 'Add_Station' in status[1]:
            logging.info(f"Adding Station {status[2]} with {status[3]} capacity in the cluster {status[4]}")
            engine = engine_creation()
            add_station(status[2],status[3],status[4],engine)
            calculate_stations_usage(engine)
            clean_queue(status)
            logging.info(f"Station {status[2]} Successfully Added")
        else:
            logging.error("No function provided, cleaning the queue")
            clean_queue(status)
    else:
        logging.info("Doing nothing")
    time.sleep(120)
