import pytest
from unittest.mock import patch, MagicMock
from script import get_kubernetes_resource
import gzip
from datetime import datetime



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