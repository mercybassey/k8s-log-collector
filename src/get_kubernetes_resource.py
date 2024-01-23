def get_kubernetes_resource(k8s_apps_v1, namespace, resource_name, resource_type):
    if resource_type == 'statefulset':
        return k8s_apps_v1.read_namespaced_stateful_set(resource_name, namespace)
    elif resource_type == 'deployment':
        return k8s_apps_v1.read_namespaced_deployment(resource_name, namespace)
    elif resource_type == 'pod':
        return k8s_apps_v1.read_namespaced_deployment(resource_name, namespace)
    else:
        raise ValueError(f"Unsupported resource type: {resource_type}")
    