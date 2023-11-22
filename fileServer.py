from flask import Flask, appcontext_popped
from flask import send_from_directory
import time
from multiprocessing import Process
import os


app = Flask(__name__)
base_url = "http://nerf-worker:5100/"
#TODO: fix this function
def to_url(file_name):
    return base_url+"/"+file_name

@app.route('/output/videos/<path:path>')
def send_video(path):
    # example path: /data/outputs/out/imgs_path_all/video.mp4
    return send_from_directory('data',path)

@app.route('/output/models/<path:path>')
def send_model(path):
    return send_from_directory('output/models',path)

def dummy_nerf():
    count = 0
    while(True):
        print(f"Job {count} Started ")
        time.sleep(1)
        print(f"Job {count} complete")
        print()
        count+=1

def start_flask():
    global app
    app.run(host="0.0.0.0", port=5200, debug=True)

# Demonstrating how files will be pulled from the cache
"""if __name__ == "__main__":
    flaskProcess = Process(target=start_flask, args= ())
    nerfProcess = Process(target=dummy_nerf, args= ())

    flaskProcess.start()
    nerfProcess.start()

    flaskProcess.join()
    nerfProcess.join()"""

