from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError, ClientError
import logging

from src.process_pod_logs import process_pod_logs
from src.get_kubernetes_resource import get_kubernetes_resource
from src.list_pods_for_resource import list_pods_for_resource

def retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name):
    try:
        resource = get_kubernetes_resource(k8s_apps_v1, k8s_core_v1, namespace, resource_name, resource_type)
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

    for pod in pods:
        try:
            process_pod_logs(k8s_core_v1, s3_client, pod, namespace, bucket_name)
        except ApiException as e:
            logging.error(f"Failed to retrieve logs for pod '{pod.metadata.name}': {e}")
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to upload logs for pod '{pod.metadata.name}' to S3: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing pod '{pod.metadata.name}': {e}")
