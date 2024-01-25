from datetime import datetime
import gzip
import io
import logging
import os


logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')


def process_pod_logs(k8s_core_v1, s3_client, pod, namespace, bucket_name):  
    pod_name = pod.metadata.name
    logs = k8s_core_v1.read_namespaced_pod_log(pod_name, namespace)
    compressed_logs = gzip.compress(logs.encode('utf-8'))
    timestamp = datetime.utcnow().isoformat()
    compressed_log_filename = f"{pod_name}-logs-{timestamp}.gz"
    s3_client.put_object(Bucket=bucket_name, Key=compressed_log_filename, Body=io.BytesIO(compressed_logs))
    logging.info(f"Logs for pod {pod_name} uploaded to S3 bucket {bucket_name} as {compressed_log_filename}")