from unittest.mock import patch, MagicMock

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '..', '..'))

from src.get_kubernetes_resource import get_kubernetes_resource



from unittest.mock import patch, MagicMock


def test_get_kubernetes_statefulset_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()  
    namespace = 'test-namespace'
    resource_name = 'test-statefulset'
    resource_type = 'statefulset'
    
    result = get_kubernetes_resource(mock_k8s_apps_v1, mock_k8s_core_v1, namespace, resource_name, resource_type)
    
    mock_k8s_apps_v1.read_namespaced_stateful_set.assert_called_with(resource_name, namespace)

def test_get_kubernetes_deployment_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()  
    namespace = 'test-namespace'
    resource_name = 'test-deployment'
    resource_type = 'deployment'

    result = get_kubernetes_resource(mock_k8s_apps_v1, mock_k8s_core_v1, namespace, resource_name, resource_type)
    
    mock_k8s_apps_v1.read_namespaced_deployment.assert_called_with(resource_name, namespace)

def test_get_kubernetes_pod_resource():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_k8s_core_v1.read_namespaced_pod = MagicMock()

    namespace = 'test-namespace'
    resource_name = 'test-pod'
    resource_type = 'pod'

    result = get_kubernetes_resource(mock_k8s_apps_v1, mock_k8s_core_v1, namespace, resource_name, resource_type)
    
    mock_k8s_core_v1.read_namespaced_pod.assert_called_with(resource_name, namespace)
