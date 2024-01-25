# Kubernetes Log Collector

## Overview

Logs are incredibly important for any application, especially when it comes to figuring out
problems as they pop up. When you're working with applications in Kubernetes, managing these
logs really well becomes super important. But here's the thing: dealing with logs in Kubernetes
can get pretty tricky, especially when your applications are churning out a ton of them over time.
It gets even tougher because these logs don't stick around forever – they disappear after a while,
making it hard to do a deep dive and really understand what's been happening.

This project tackles the task of collecting logs by making the whole process a lot simpler,
whether we're talking about individual pods or ones that are part of a specific Kubernetes Deployment
or StatefulSet. It smartly compresses these logs to make them smaller and then sends them off to a safe and
central spot – an AWS S3 bucket. This way, all those important historical logs are kept safe and sound,
and teams can easily grab them as gzip files whenever they need to dive deep into serious log analysis.

This project is suitable for running within a Kubernetes cluster, leveraging the cluster's service account
for Kubernetes API authentication.

## Features

- Supports collecting logs from both Kubernetes standalone Pods, Deployments and StatefulSets.
- Compresses the collected logs using gzip for efficient storage.
- Upload the compressed logs to a specified AWS S3 bucket.
- Error handling and logging for troubleshooting.

## Prerequisites

- Access to a Kubernetes cluster with permissions to create CronJobs.
- An AWS account with an S3 bucket configured.

## Configuration

The script uses environment variables for configuration, which can be set as environment variables
in a Kubernetes CronJob manifest for deployment.

## Environment Variables

- `AWS_ACCESS_KEY_ID`: AWS access key ID.
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key.
- `AWS_REGION`: AWS region where the S3 bucket is located.
- `NAMESPACE`: Kubernetes namespace of the target resource.
- `RESOURCE_TYPE`: Type of the Kubernetes resource (deployment or statefulset).
- `RESOURCE_NAME`: Name of the Kubernetes resource (Deployment or StatefulSet).
- `BUCKET_NAME`: Name of the AWS S3 bucket for log storage.


## Kubernetes Deployment

### RBAC Configuration

Before deploying the script, set up the necessary RBAC permissions:

1. Create a ClusterRole:

Define a ClusterRole with the necessary permissions to access the required Kubernetes resources.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: log-collector-clusterrole
rules:
- apiGroups: ["apps"]
  resources: ["pods", "statefulsets", "deployments"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
```

Apply this configuration with `kubectl apply -f clusterrole.yaml`.

2. Create a ClusterRoleBinding:
Bind the ClusterRole to the service account that the script will use.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: log-collector-clusterrolebinding
subjects:
- kind: ServiceAccount
  name: default  # Replace with your ServiceAccount name if not using the default
  namespace: default  # Replace with the namespace where your ServiceAccount is located
roleRef:
  kind: ClusterRole
  name: log-collector-clusterrole
  apiGroup: rbac.authorization.k8s.io

```

Apply this configuration with `kubectl apply -f clusterrolebinding.yaml`.

## Deploy the CronJob

1. Create a Kubernetes Secret for AWS Credentials:

```command
kubectl create secret generic aws-credentials \
  --from-literal=aws_access_key_id=your-access-key-id \
  --from-literal=aws_secret_access_key=your-secret-access-key
```

2. Deploy the CronJob:

Create a Kubernetes manifest file and ensure all environment variables are correctly set:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: log-collector-job
spec:
  schedule: "*/30 * * * *"  # This schedule runs the job every 30 minutes. Adjust as needed.
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: log-collector
            image: mercybassey/k8s-log-collector:latest
            env:
              - name: AWS_ACCESS_KEY_ID
                valueFrom:
                  secretKeyRef:
                    name: aws-credentials
                    key: aws_access_key_id
              - name: AWS_SECRET_ACCESS_KEY
                valueFrom:
                  secretKeyRef:
                    name: aws-credentials
                    key: aws_secret_access_key
              - name: AWS_REGION
                value: "your-region"
              - name: NAMESPACE
                value: "your-namespace"
              - name: RESOURCE_TYPE
                value: "pod"  # or "statefulset" or "deployment"
              - name: RESOURCE_NAME
                value: "name of the deployment or statefulset"
              - name: BUCKET_NAME
                value: "your-aws-bucket-name"
          restartPolicy: OnFailure
```

Save this manifest to a file, e.g., `log-collector-cronjob.yaml`, and deploy
the CronJob to your Kubernetes cluster with `kubectl apply -f log-collector-cronjob.yaml`.

## Notes

- `Schedule`: The schedule field is a cron expression that determines how often the job runs.
The example `*/30 * * * *` means the job will run every thirty minutes. You can adjust this to suit your needs.

- `Environment Variables`: The manifest sets environment variables from the Kubernetes secret `aws-credentials` for AWS credentials. Other environment - - variables are to be set directly.
- `Restart Policy`: The restartPolicy is set to OnFailure, meaning Kubernetes will restart the job if it fails.

## Deploying the CronJob

- Save this manifest to a file, e.g., `log-collector-cronjob.yaml`.
- Deploy the CronJob to your Kubernetes cluster:

```command
kubectl apply -f log-collector-cronjob.yaml
```

This will create a CronJob in your Kubernetes cluster that periodically
runs the log collector script according to the specified schedule.

## Viewing Logs

To monitor the operation of the script or troubleshoot any issue,
you can view the logs of the CronJob pods.
This can provide valuable information into the script's execution
and help identify any errors or issues that may occur.

Follow these steps to view the logs of a specific pod created by the CronJob:

1. First, find the pods that have been created by the CronJob. You can list all pods
in the namespace and find the ones related to your CronJob:

```command
# If your pod is in the default namespace
kubectl get pods

# If your CronJob pod is in a different namespace
kubectl get pods -n <namespace>
```

Replace `<namespace>` with the namespace where your CronJob is running.

2. Once you have identified the pod, use the kubectl logs command to view its logs:

```command
# If your pod is in the default namespace
kubectl logs <pod-name>

# If your CronJob pod is in a different namespace
kubectl logs <pod-name> -n <namespace>
```

Replace `<pod-name>` with the name of the pod you want to check, and `<namespace>` with the namespace of the pod.

## How to Contribute

- Create an Issue
- Wait for Issue Approval 
- Fork the Repository
- Clone your Fork
- Create a new branch
- Make your change
- Test your change
- Commit your change
- Create a Pull Request

To ensure everything works smoothly, remember to provide access credentials and include all the necessary environment variables when you're testing. Also, it's really important that you add tests for any changes you make. This helps me maintain the quality and reliability of this project. Thanks for contributing!