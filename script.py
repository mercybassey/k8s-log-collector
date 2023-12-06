from kubernetes import client
from kubernetes.client.rest import ApiException

from botocore.exceptions import BotoCoreError, ClientError
import boto3

import gzip
import io
from datetime import datetime
import logging

from dotenv import load_dotenv
import os

k8s_apps_v1 = client.AppsV1Api()
k8s_core_v1 = client.CoreV1Api()

# AWS credentials and region
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION', 'default-region')

# Kubernetes and S3 configurations
namespace = os.getenv('NAMESPACE', 'default-namespace')
resource_type = os.getenv('RESOURCE_TYPE', 'deployment').lower()
resource_name = os.getenv('RESOURCE_NAME', 'default-resource')
bucket_name = os.getenv('BUCKET_NAME', 'default-bucket')

# Initializing the S3 client
s3_client = boto3.client('s3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

bucket_name = "postgres-database-logs"

# Set up basic logging
logging.basicConfig(level=logging.INFO, 
    filename='postgres.log', 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name):
    try:
        # Determine the resource type and retrieve the corresponding Kubernetes resource
        if resource_type == 'statefulset':
            resource = k8s_apps_v1.read_namespaced_stateful_set(resource_name, namespace)
        elif resource_type == 'deployment':
            resource = k8s_apps_v1.read_namespaced_deployment(resource_name, namespace)
        else:
            logging.error(f"Unsupported resource type: {resource_type}")
            return

        # Extract the pod labels from the resource's spec
        pod_labels = resource.spec.selector.match_labels
        label_selector = ','.join([f'{k}={v}' for k, v in pod_labels.items()])

        # List the pods based on the label selector
        pods = k8s_core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
    except ApiException as e:
        logging.error(f"Failed to retrieve {resource_type} '{resource_name}' in namespace '{namespace}': {e}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return

    # Iterate over each pod and process its logs
    for pod in pods.items:
        pod_name = pod.metadata.name
        try:
            # Retrieve logs from the current pod
            logs = k8s_core_v1.read_namespaced_pod_log(pod_name, namespace)

            # Compress the logs using gzip
            compressed_logs = gzip.compress(logs.encode('utf-8'))

            # Generate a timestamped filename for the compressed logs
            timestamp = datetime.now().isoformat()
            compressed_log_filename = f"{pod_name}-logs-{timestamp}.gz"

            # Upload the compressed logs to the specified S3 bucket
            s3_client.put_object(Bucket=bucket_name, Key=compressed_log_filename, Body=io.BytesIO(compressed_logs))
            logging.info(f"Logs for pod {pod_name} uploaded to S3 bucket {bucket_name} as {compressed_log_filename}")
        except ApiException as e:
            logging.error(f"Failed to retrieve logs for pod '{pod_name}': {e}")
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to upload logs for pod '{pod_name}' to S3: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing pod '{pod_name}': {e}")


retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name)

