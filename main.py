from flask import Flask
from flask import send_from_directory
from pathlib import Path
import requests
import pika
import json
import time
from multiprocessing import Process, connection
import os

app = Flask(__name__)
base_url = "http://localhost:5100/"

def nerf_worker():
    channel = connection.channel()
    channel.queue_declare(queue = 'sfm_in')
    channel.queue_declare(queue = 'sfm_out')

    def process_nerf_worker(ch, method, properties, body):

        #TODO: not sure what data is needed for nerf to run
        nerf_data = json.load(body)
        id = nerf_data["id"]
        width = nerf_data["vid_width"]
        height = nerf_data["vid_height"]
        intrinsic_matrix = nerf_data["intrinsic_matrix"]
        frames = nerf_data["frames"]
        for i in frames:
            url = requests.get(frames["file_path"])





        #TODO: call nerf to do smthing
        nerf_vid_filepath = nerf()
        rendered_vid = requests.get(nerf_vid_filepath)


        #create dict for output video and filepath
        nerf_output_object = {"model_filepath" : nerf_vid_filepath, "rendered_vid" : rendered_vid}
        channel.basic_publish(exchange='', routing_key='nerf-out', body= nerf_output_object)

        # confirm to rabbitmq job is done
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":


        