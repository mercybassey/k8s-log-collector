import pytest
from unittest.mock import patch, MagicMock
from script import initialize_clients, get_kubernetes_resource

def test_initialize_clients():
    with patch('script.config.load_incluster_config'), \
         patch('script.client.AppsV1Api', return_value=MagicMock()) as mock_apps_v1_api, \
         patch('script.client.CoreV1Api', return_value=MagicMock()) as mock_core_v1_api, \
         patch('script.boto3.client', return_value=MagicMock()) as mock_s3_client:

        # Call the function
        k8s_apps_v1, k8s_core_v1, s3_client = initialize_clients()

        # Check if the mock objects were called
        assert mock_apps_v1_api.called
        assert mock_core_v1_api.called
        assert mock_s3_client.called

        # Check if the returned objects are instances of MagicMock
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

    # Assert that the mock method was called with correct parameters
    mock_k8s_apps_v1.read_namespaced_stateful_set.assert_called_with(resource_name, namespace)

def  test_get_kubernetes_deployment_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_apps_v1.read_namespaced_deployment = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-deployment'
    resource_type = 'deployment'

    result = get_kubernetes_resource(mock_k8s_apps_v1, namespace, resource_name, resource_type)

    # Assert that the mock method was called with correct parameters
    mock_k8s_apps_v1.read_namespaced_deployment.assert_called_with(resource_name, namespace)

       
