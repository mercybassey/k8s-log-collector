from unittest.mock import patch, MagicMock

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '..', '..'))

from src.initialize_clients import initialize_clients



def test_initialize_clients():
    with patch('src.initialize_clients.config.load_incluster_config'), \
         patch('src.initialize_clients.client.AppsV1Api', return_value=MagicMock()) as mock_apps_v1_api, \
         patch('src.initialize_clients.client.CoreV1Api', return_value=MagicMock()) as mock_core_v1_api, \
         patch('src.initialize_clients.boto3.client', return_value=MagicMock()) as mock_s3_client:

       
        k8s_apps_v1, k8s_core_v1, s3_client = initialize_clients()

        assert mock_apps_v1_api.called
        assert mock_core_v1_api.called
        assert mock_s3_client.called

        assert isinstance(k8s_apps_v1, MagicMock)
        assert isinstance(k8s_core_v1, MagicMock)
        assert isinstance(s3_client, MagicMock)










