from unittest.mock import patch, MagicMock
from script import initialize_clients



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










