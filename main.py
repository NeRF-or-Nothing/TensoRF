from flask import Flask
from flask import send_from_directory
from pathlib import Path
import requests
import pika
import json
import time
from multiprocessing import Process, connection
import os
from dataLoader import sfm2nerf
from opt import config_parser
from worker import train_tensorf

app = Flask(__name__)
#base_url = "http://localhost:5200/"
#base_url = "host.docker.internal:5200/"
base_url = "0.0.0.0:5200/"

def nerf_worker():
    # TODO: Communicate with rabbitmq server on port defined in web-server arguments
    # Also, get rid of plaintext `credentials` and use a config file
    print("Starting nerf_worker!")

    #rabbitmq_domain = "rabbitmq"
    rabbitmq_domain = "localhost"
    credentials = pika.PlainCredentials('admin', 'password123')
    parameters = pika.ConnectionParameters(
      rabbitmq_domain, 5672, '/', credentials, heartbeat=300
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue = 'nerf-in')
    channel.queue_declare(queue = 'nerf-out')
    print("DEBUG: Connected to RabbitMQ", flush=True)

    def process_nerf_worker(ch, method, properties, body):

        job_data = json.loads(body.decode())
        print(f"DEBUG: Running New Job With ID: {job_data['id']}")
        print("DEBUG: job_data = ", job_data, flush=True)
        print("Starting New Nerf Job!")

        #TODO: not sure what data is needed for nerf to run
        # get data from rabbitmq
        nerf_data = json.loads(body)
        id = nerf_data["id"]  
        width = nerf_data["vid_width"]
        height = nerf_data["vid_height"]
        intrinsic_matrix = nerf_data["intrinsic_matrix"]
        frames = nerf_data["frames"]
        jobdir = Path(f"data/sfm_data/{id}")
        if not jobdir.exists():
          os.makedirs(jobdir)
        print(f"DEBUG: len(frames)={len(frames)}", flush=True)
        
        for i, fr_ in enumerate(frames):
            # Save copy of motion data
            url = fr_["file_path"]
            print(f"DEBUG: url={url}", flush=True)
            
            # TODO: Add compatibility for both docker and local 
            url = url.replace("host.docker.internal", "0.0.0.0")
            print(f"DEBUG: url2{url}", flush=True)
            img = requests.get(url)
            # save img to jobdir and replace old file path with local file path
            fr_["file_path"] = f"{i}.png"
            img_file_path = jobdir / fr_["file_path"]
            img_file_path.write_bytes(img.content)

        jobdir2 = jobdir / f"transforms_train.json"
        jobdir2.write_text(json.dumps(nerf_data, indent=4))
        args = config_parser("--config configs/localworkerconfig.txt")
        args.datadir += f"/{id}"
        args.expname = id
        print(f"DEBUG: args={args}", flush=True)
        logfolder, tensorf_model = train_tensorf(args)
        
        return
        #TODO: get nerf video and submit to rabbitmq


        #create dict for output video and filepath
        nerf_output_object = {"model_filepath" : nerf_vid_filepath, "rendered_vid" : rendered_vid}
        channel.basic_publish(exchange='', routing_key='nerf-out', body= nerf_output_object)

        # confirm to rabbitmq job is done
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='nerf-in', on_message_callback=process_nerf_worker, auto_ack=False)
    channel.start_consuming()
    # Should not get here!


def start_flask():
    global app
    app.run(host="0.0.0.0", port=5200, debug=True)


if __name__ == "__main__":
    print("~NERF WORKER~")
    nerfProcess = Process(target=nerf_worker, args=())
    flaskProcess = Process(target=start_flask, args=())
    flaskProcess.start()
    nerfProcess.start()
    flaskProcess.join()
    nerfProcess.join()

        