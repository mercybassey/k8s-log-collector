import pytest
from unittest.mock import patch, MagicMock

import io
import gzip
from freezegun import freeze_time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from script import process_pod_logs



def test_process_pod_logs():
    
    mock_k8s_core_v1 = MagicMock()
    mock_s3_client = MagicMock()
    mock_pod = MagicMock()
    mock_pod.metadata.name = 'test-pod'

    namespace = 'test-namespace'
    bucket_name = 'test-bucket'

    
    mock_k8s_core_v1.read_namespaced_pod_log.return_value = 'log data'

    with patch('gzip.compress'), patch('io.BytesIO'), freeze_time("2023-01-01"):
        
        process_pod_logs(mock_k8s_core_v1, mock_s3_client, mock_pod, namespace, bucket_name)

        mock_k8s_core_v1.read_namespaced_pod_log.assert_called_with('test-pod', namespace)
        compressed_log_filename = f"test-pod-logs-2023-01-01T00:00:00.gz"
        mock_s3_client.put_object.assert_called_with(
            Bucket=bucket_name,
            Key=compressed_log_filename,
            Body=io.BytesIO(gzip.compress('log data'.encode('utf-8')))
        )
