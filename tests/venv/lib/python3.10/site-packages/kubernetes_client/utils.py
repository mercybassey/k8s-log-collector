
import os

def is_running_in_k8s():
    return os.path.isdir("/var/run/secrets/kubernetes.io/")
