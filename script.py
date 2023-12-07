from kubernetes import client, config
from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError, ClientError
import boto3
import gzip
import io
from datetime import datetime
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_clients():
    """Initializes and returns Kubernetes and AWS S3 clients."""
    config.load_incluster_config()
    k8s_apps_v1 = client.AppsV1Api()
    k8s_core_v1 = client.CoreV1Api()

    # AWS credentials and region
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region_name = os.getenv('AWS_REGION', 'default-region')

    # Initializing the S3 client
    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    return k8s_apps_v1, k8s_core_v1, s3_client

def get_kubernetes_resource(k8s_apps_v1, namespace, resource_name, resource_type):
    """Retrieves a specified resource from Kubernetes."""
    if resource_type == 'statefulset':
        return k8s_apps_v1.read_namespaced_stateful_set(resource_name, namespace)
    elif resource_type == 'deployment':
        return k8s_apps_v1.read_namespaced_deployment(resource_name, namespace)
    else:
        raise ValueError(f"Unsupported resource type: {resource_type}")

def list_pods_for_resource(k8s_core_v1, namespace, resource):
    """Lists pods for a given Kubernetes resource."""
    pod_labels = resource.spec.selector.match_labels
    label_selector = ','.join([f'{k}={v}' for k, v in pod_labels.items()])
    return k8s_core_v1.list_namespaced_pod(namespace, label_selector=label_selector)

def process_pod_logs(k8s_core_v1, s3_client, pod, namespace, bucket_name):
    """Processes and uploads logs for a given pod."""
    pod_name = pod.metadata.name
    logs = k8s_core_v1.read_namespaced_pod_log(pod_name, namespace)
    compressed_logs = gzip.compress(logs.encode('utf-8'))
    timestamp = datetime.now().isoformat()
    compressed_log_filename = f"{pod_name}-logs-{timestamp}.gz"
    s3_client.put_object(Bucket=bucket_name, Key=compressed_log_filename, Body=io.BytesIO(compressed_logs))
    logging.info(f"Logs for pod {pod_name} uploaded to S3 bucket {bucket_name} as {compressed_log_filename}")

def retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name):
    """Retrieves and uploads logs for specified Kubernetes resources."""
    try:
        resource = get_kubernetes_resource(k8s_apps_v1, namespace, resource_name, resource_type)
        pods = list_pods_for_resource(k8s_core_v1, namespace, resource)
    except ApiException as e:
        logging.error(f"Failed to retrieve {resource_type} '{resource_name}' in namespace '{namespace}': {e}")
        return
    except ValueError as e:
        logging.error(e)
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return

    for pod in pods.items:
        try:
            process_pod_logs(k8s_core_v1, s3_client, pod, namespace, bucket_name)
        except ApiException as e:
            logging.error(f"Failed to retrieve logs for pod '{pod.metadata.name}': {e}")
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to upload logs for pod '{pod.metadata.name}' to S3: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing pod '{pod.metadata.name}': {e}")

def main():
    """Main function to execute script logic."""
    k8s_apps_v1, k8s_core_v1, s3_client = initialize_clients()

    # Kubernetes and S3 configurations
    namespace = os.getenv('NAMESPACE', 'default').lower()
    resource_type = os.getenv('RESOURCE_TYPE', 'deployment').lower()
    resource_name = os.getenv('RESOURCE_NAME').lower()
    bucket_name = os.getenv('BUCKET_NAME').lower()

    retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name)

if __name__ == "__main__":
    main()
