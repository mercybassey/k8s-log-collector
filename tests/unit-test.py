import pytest
from unittest.mock import patch, MagicMock
from script import initialize_clients, get_kubernetes_resource, list_pods_for_resource,  process_pod_logs, retrieve_and_upload_logs
import io
import gzip
from datetime import datetime
from freezegun import freeze_time

from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError, ClientError
import logging

def test_initialize_clients():
    with patch('script.config.load_incluster_config'), \
         patch('script.client.AppsV1Api', return_value=MagicMock()) as mock_apps_v1_api, \
         patch('script.client.CoreV1Api', return_value=MagicMock()) as mock_core_v1_api, \
         patch('script.boto3.client', return_value=MagicMock()) as mock_s3_client:

       
        k8s_apps_v1, k8s_core_v1, s3_client = initialize_clients()

     
        assert mock_apps_v1_api.called
        assert mock_core_v1_api.called
        assert mock_s3_client.called

        
        assert isinstance(k8s_apps_v1, MagicMock)
        assert isinstance(k8s_core_v1, MagicMock)
        assert isinstance(s3_client, MagicMock)

def test_get_kubernetes_statefulset_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_apps_v1.read_namespaced_stateful_set = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-statefulset'
    resource_type = 'statefulset'

    
    result = get_kubernetes_resource(mock_k8s_apps_v1, namespace, resource_name, resource_type)

    
    mock_k8s_apps_v1.read_namespaced_stateful_set.assert_called_with(resource_name, namespace)

def  test_get_kubernetes_deployment_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_apps_v1.read_namespaced_deployment = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-deployment'
    resource_type = 'deployment'

    result = get_kubernetes_resource(mock_k8s_apps_v1, namespace, resource_name, resource_type)

    
    mock_k8s_apps_v1.read_namespaced_deployment.assert_called_with(resource_name, namespace)

def test_list_pods_for_resource():
    mock_k8s_core_v1 = MagicMock()
    mock_resource = MagicMock()
    mock_resource.spec.selector.match_labels = {'key1': 'value1', 'key2': 'value2'}
    namespace = 'test-namespace'

   
    list_pods_for_resource(mock_k8s_core_v1, namespace, mock_resource)


    expected_label_selector = 'key1=value1,key2=value2'

    
    mock_k8s_core_v1.list_namespaced_pod.assert_called_with(namespace, label_selector=expected_label_selector)

def test_process_pod_logs():
    
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    namespace = 'test-namespace'
    bucket_name = 'test-bucket'

    
    mock_k8s_core_v1.read_namespaced_pod_log.return_value = 'log data'

    with patch('gzip.compress'), patch('io.BytesIO'), freeze_time("2023-01-01"):
        
        process_pod_logs(mock_k8s_core_v1, mock_s3_client, mock_pod, namespace, bucket_name)

        mock_k8s_core_v1.read_namespaced_pod_log.assert_called_with('test-pod', namespace)
        compressed_log_filename = f"test-pod-logs-2023-01-01T00:00:00.gz"
        mock_s3_client.put_object.assert_called_with(
            Bucket=bucket_name,
            Key=compressed_log_filename,
            Body=io.BytesIO(gzip.compress('log data'.encode('utf-8')))
        )

def test_retrieve_and_upload_logs_success():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    with patch('script.get_kubernetes_resource', return_value=MagicMock()) as mock_get_resource, \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[mock_pod])) as mock_list_pods, \
         patch('script.process_pod_logs') as mock_process_logs, \
         patch('logging.error') as mock_logging_error:

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        mock_get_resource.assert_called_with(mock_k8s_apps_v1, namespace, resource_name, resource_type)
        mock_list_pods.assert_called_with(mock_k8s_core_v1, namespace, mock_get_resource.return_value)
        mock_process_logs.assert_called_with(mock_k8s_core_v1, mock_s3_client, mock_pod, namespace, bucket_name)
        mock_logging_error.assert_not_called()

def test_retrieve_and_upload_logs_api_exception(caplog):  
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'

    with patch('script.get_kubernetes_resource', side_effect=ApiException("API error")):
        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        # Checking the presence of key parts of the message separately
        assert "Failed to retrieve deployment" in caplog.text
        assert "'test-resource'" in caplog.text
        assert "in namespace 'test-namespace'" in caplog.text
        assert "API error" in caplog.text



  
