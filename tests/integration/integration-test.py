from unittest.mock import patch, MagicMock
from moto import mock_s3
import boto3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import script


@mock_s3
def test_integration():
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')

    env_vars = {
        'AWS_ACCESS_KEY_ID': 'testkey',
        'AWS_SECRET_ACCESS_KEY': 'testsecret',
        'AWS_REGION': 'us-east-1',
        'NAMESPACE': 'test-namespace',
        'RESOURCE_TYPE': 'deployment',
        'RESOURCE_NAME': 'test-resource',
        'BUCKET_NAME': 'test-bucket'
    }

    
    with patch('src.initialize_clients.client.AppsV1Api') as mock_k8s_apps_v1, \
         patch('src.initialize_clients.client.CoreV1Api') as mock_k8s_core_v1, \
         patch('src.initialize_clients.config.load_incluster_config'), \
         patch.dict('os.environ', env_vars, clear=True):

        mock_resource = MagicMock()
        mock_resource.spec.selector.match_labels = {'app': 'test-app'}
        mock_k8s_apps_v1.return_value.read_namespaced_deployment.return_value = mock_resource
        mock_k8s_core_v1.return_value.list_namespaced_pod.return_value = MagicMock(items=[MagicMock()])

        script.main()

        mock_k8s_apps_v1.return_value.read_namespaced_deployment.assert_called_with('test-resource', 'test-namespace')
        mock_k8s_core_v1.return_value.list_namespaced_pod.assert_called_once()

