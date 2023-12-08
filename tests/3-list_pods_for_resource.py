from unittest.mock import MagicMock
from script import list_pods_for_resource



def test_list_pods_for_resource():
    mock_k8s_core_v1 = MagicMock()
    mock_resource = MagicMock()
    mock_resource.spec.selector.match_labels = {'key1': 'value1', 'key2': 'value2'}
    namespace = 'test-namespace'

   
    list_pods_for_resource(mock_k8s_core_v1, namespace, mock_resource)


    expected_label_selector = 'key1=value1,key2=value2'

    
    mock_k8s_core_v1.list_namespaced_pod.assert_called_with(namespace, label_selector=expected_label_selector)