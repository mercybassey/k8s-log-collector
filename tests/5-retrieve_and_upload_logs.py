import pytest
from unittest.mock import patch, MagicMock
from moto import mock_s3
import boto3
from script import retrieve_and_upload_logs
from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError

def setup_mock_s3():
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    return s3

@mock_s3
def test_retrieve_and_upload_logs_log_upload_failure(caplog):
    s3 = setup_mock_s3()
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    with patch('script.get_kubernetes_resource', return_value=MagicMock()), \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[mock_pod])), \
         patch('script.process_pod_logs', side_effect=BotoCoreError):

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, s3, namespace, resource_name, resource_type, bucket_name)

        assert "Failed to upload logs for pod" in caplog.text

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

        assert "Failed to retrieve deployment" in caplog.text
        assert "'test-resource'" in caplog.text
        assert "in namespace 'test-namespace'" in caplog.text
        assert "API error" in caplog.text

def test_retrieve_and_upload_logs_value_error(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'

    with patch('script.get_kubernetes_resource', side_effect=ValueError("Custom error message")):
        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        assert "Custom error message" in caplog.text

def test_retrieve_and_upload_logs_other_exception(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'

    with patch('script.get_kubernetes_resource', side_effect=Exception("Unexpected error")):
        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        assert "An unexpected error occurred: Unexpected error" in caplog.text

def test_retrieve_and_upload_logs_success(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'

    with patch('script.get_kubernetes_resource', return_value=MagicMock()), \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[MagicMock(), MagicMock()])), \
         patch('script.process_pod_logs') as mock_process_logs:

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        assert mock_process_logs.call_count == 2