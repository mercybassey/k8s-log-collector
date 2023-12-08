import pytest
from unittest.mock import patch, MagicMock
from script import retrieve_and_upload_logs
from datetime import datetime


from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError


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


def test_retrieve_and_upload_logs_log_upload_failure(caplog):
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
         patch('script.process_pod_logs', side_effect=BotoCoreError) as mock_process_logs:

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        # Assertions
        mock_get_resource.assert_called_with(mock_k8s_apps_v1, namespace, resource_name, resource_type)
        mock_list_pods.assert_called_with(mock_k8s_core_v1, namespace, mock_get_resource.return_value)
        mock_process_logs.assert_called_with(mock_k8s_core_v1, mock_s3_client, mock_pod, namespace, bucket_name)
        
        # Check for a general error log message related to processing/uploading logs
        assert "Failed to upload logs for pod" in caplog.text

def test_retrieve_and_upload_logs_success(caplog):
    # Mock setup
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

        assert mock_process_logs.call_count == 2  # Assuming two pods in items



def test_retrieve_and_upload_logs_api_exception(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    # Simulate ApiException in process_pod_logs
    with patch('script.get_kubernetes_resource', return_value=MagicMock()), \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[mock_pod])), \
         patch('script.process_pod_logs', side_effect=ApiException("API error")):

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        # Check if the expected error message is in the log output
        assert "Failed to retrieve logs for pod 'test-pod'" in caplog.text

def test_retrieve_and_upload_logs_s3_upload_error(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    # Simulate BotoCoreError in process_pod_logs
    with patch('script.get_kubernetes_resource', return_value=MagicMock()), \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[mock_pod])), \
         patch('script.process_pod_logs', side_effect=BotoCoreError):

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        # Check if an error log for S3 upload failure was made
        assert "Failed to upload logs for pod 'test-pod'" in caplog.text

def test_retrieve_and_upload_logs_unexpected_error(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    with patch('script.get_kubernetes_resource', return_value=MagicMock()), \
         patch('script.list_pods_for_resource', return_value=MagicMock(items=[mock_pod])), \
         patch('script.process_pod_logs', side_effect=Exception("Unexpected error")):

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        # Check if an error log for unexpected error was made
        assert "An unexpected error occurred while processing pod 'test-pod'" in caplog.text