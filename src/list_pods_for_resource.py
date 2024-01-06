def list_pods_for_resource(k8s_core_v1, namespace, resource):
    pod_labels = resource.spec.selector.match_labels
    label_selector = ','.join([f'{k}={v}' for k, v in pod_labels.items()])
    return k8s_core_v1.list_namespaced_pod(namespace, label_selector=label_selector)