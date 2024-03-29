import pytest
from unittest.mock import patch, MagicMock
from moto import mock_s3
import boto3
from kubernetes.client.rest import ApiException
from botocore.exceptions import BotoCoreError

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '..', '..'))

from src.retrieve_and_upload_logs import retrieve_and_upload_logs

@pytest.fixture
def setup_mock_s3():
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')
        yield s3

@mock_s3
def test_retrieve_and_upload_logs_log_upload_failure(caplog, setup_mock_s3):
    s3 = setup_mock_s3
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    with patch('src.retrieve_and_upload_logs.get_kubernetes_resource', return_value=MagicMock()), \
         patch('src.retrieve_and_upload_logs.list_pods_for_resource', return_value=[mock_pod]), \
         patch('src.retrieve_and_upload_logs.process_pod_logs', side_effect=BotoCoreError):

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, s3, namespace, resource_name, resource_type, bucket_name)

        assert "Failed to upload logs for pod 'test-pod'" in caplog.text

def test_retrieve_and_upload_logs_api_exception(caplog):
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'

    with patch('src.retrieve_and_upload_logs.get_kubernetes_resource', side_effect=ApiException("API error")):
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

    with patch('src.retrieve_and_upload_logs.get_kubernetes_resource', side_effect=ValueError("Custom error message")):
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

    with patch('src.retrieve_and_upload_logs.get_kubernetes_resource', side_effect=Exception("Unexpected error")):
        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client, namespace, resource_name, resource_type, bucket_name)

        assert "An unexpected error occurred: Unexpected error" in caplog.text

       
def test_retrieve_and_upload_logs_success(setup_mock_s3):
    s3 = setup_mock_s3
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    namespace = 'test-namespace'
    resource_name = 'test-resource'
    resource_type = 'deployment'
    bucket_name = 'test-bucket'
    mock_pod1 = MagicMock()
    mock_pod1.metadata.name = 'test-pod1'
    mock_pod2 = MagicMock()
    mock_pod2.metadata.name = 'test-pod2'

    with patch('src.retrieve_and_upload_logs.get_kubernetes_resource', return_value=MagicMock()), \
         patch('src.retrieve_and_upload_logs.list_pods_for_resource', return_value=[mock_pod1, mock_pod2]), \
         patch('src.retrieve_and_upload_logs.process_pod_logs') as mock_process_logs:

        retrieve_and_upload_logs(mock_k8s_apps_v1, mock_k8s_core_v1, s3, namespace, resource_name, resource_type, bucket_name)

        assert mock_process_logs.call_count == 2
