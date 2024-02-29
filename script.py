import os

from src.initialize_clients import initialize_clients
from src.retrieve_and_upload_logs import retrieve_and_upload_logs

def main():
    k8s_apps_v1, k8s_core_v1, s3_client = initialize_clients()

    
    namespace = os.getenv('NAMESPACE', 'default').lower()
    resource_type = os.getenv('RESOURCE_TYPE', 'deployment').lower()
    resource_name = os.getenv('RESOURCE_NAME').lower()
    bucket_name = os.getenv('BUCKET_NAME').lower()

    retrieve_and_upload_logs(k8s_apps_v1, k8s_core_v1, s3_client, namespace, resource_name, resource_type, bucket_name)

if __name__ == "__main__":
    main()
