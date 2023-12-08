import pytest
from unittest.mock import patch, MagicMock
from moto import mock_s3
import boto3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src import script


@mock_s3
def test_integration():
    # Set up mock S3
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')

    # Define environment variables
    env_vars = {
        'AWS_ACCESS_KEY_ID': 'testkey',
        'AWS_SECRET_ACCESS_KEY': 'testsecret',
        'AWS_REGION': 'us-east-1',
        'NAMESPACE': 'test-namespace',
        'RESOURCE_TYPE': 'deployment',
        'RESOURCE_NAME': 'test-resource',
        'BUCKET_NAME': 'test-bucket'
    }

    # Mock Kubernetes API calls and configuration loading
    with patch('script.client.AppsV1Api') as mock_k8s_apps_v1, \
         patch('script.client.CoreV1Api') as mock_k8s_core_v1, \
         patch('script.config.load_incluster_config'), \
         patch.dict('os.environ', env_vars, clear=True):

        mock_resource = MagicMock()
        mock_resource.spec.selector.match_labels = {'app': 'test-app'}
        mock_k8s_apps_v1.return_value.read_namespaced_deployment.return_value = mock_resource
        mock_k8s_core_v1.return_value.list_namespaced_pod.return_value = MagicMock(items=[MagicMock()])

        # Execute the main function
        script.main()

        # Assertions to check if the main function behaved as expected
        mock_k8s_apps_v1.return_value.read_namespaced_deployment.assert_called_with('test-resource', 'test-namespace')
        mock_k8s_core_v1.return_value.list_namespaced_pod.assert_called_once()

