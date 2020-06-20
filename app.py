from data_bike import app
from config import config_data
import requests
import threading
import time

# def start_runner():
#     def start_loop():
#         not_started = True
#         while not_started:
#             print('In start loop')
#             try:
#                 r = requests.get('http://localhost:8080/')
#                 if r.status_code == 200:
#                     print('Server started, quiting start_loop')
#                     not_started = False
#                 print(r.status_code)
#             except:
#                 print('Server not yet started')
#             time.sleep(5)

#     print('Started runner')
#     thread = threading.Thread(target=start_loop)
#     thread.start()

if __name__ == "__main__":
    # # webbrowser.open('http://localhost:8080/')
    # r = requests.get('http://localhost:8080/')
    # start_runner()
    app.run(host='0.0.0.0', port=8080, debug=config_data['DEBUG'])