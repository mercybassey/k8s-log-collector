import sys
from unittest.mock import patch, MagicMock
import os

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from script import main 

def test_main():
    mock_k8s_apps_v1 = MagicMock()
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()

    with patch('script.initialize_clients', return_value=(mock_k8s_apps_v1, mock_k8s_core_v1, mock_s3_client)), \
        patch('os.getenv', side_effect=lambda k, default=None: {
        'NAMESPACE': 'test-namespace',
        'RESOURCE_TYPE': 'deployment',
        'RESOURCE_NAME': 'test-resource',
        'BUCKET_NAME': 'test-bucket'}.get(k, default)
        ), \
        patch('script.retrieve_and_upload_logs') as mock_retrieve_and_upload_logs:

        main()

        mock_retrieve_and_upload_logs.assert_called_once_with(
            mock_k8s_apps_v1, 
            mock_k8s_core_v1, mock_s3_client, 
            'test-namespace', 'test-resource', 'deployment', 'test-bucket'
        )
