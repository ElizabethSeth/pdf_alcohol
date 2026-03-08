from google.cloud import pubsub_v1
import subprocess
import os

project_id = "natural-choir-480612-m8"
subscription_id = "run-pipeline-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print("Pipeline trigger received")
    subprocess.run(["/home/maxxxvint/pdf_alcohol/run_pipeline.sh"])
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

print("Listening for messages...")
streaming_pull_future.result()