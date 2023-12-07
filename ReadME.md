# Kubernetes Log Collector

## Overview

This Python script is designed to collect logs from pods within a specified Kubernetes
Deployment or StatefulSet, compress them, and upload the compressed logs to an AWS S3 bucket.
It's suitable for running within a Kubernetes cluster, leveraging the cluster's service account
for Kubernetes API authentication.

## Features

- Supports collecting logs from both Kubernetes Deployments and StatefulSets.
- Compresses the collected logs using gzip for efficient storage.
- Uploads the compressed logs to a specified AWS S3 bucket.
- Robust error handling and logging for troubleshooting.

## Prerequisites

- Access to a Kubernetes cluster with permissions to create CronJobs.
- An AWS account with an S3 bucket configured.
- Python 3.x for local development and testing.

## Configuration

The script uses environment variables for configuration, which can be set in a .env file
for local development or in the Kubernetes CronJob manifest for deployment.

## Environment Variables

- `AWS_ACCESS_KEY_ID`: AWS access key ID.
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key.
- `AWS_REGION`: AWS region where the S3 bucket is located.
- `NAMESPACE`: Kubernetes namespace of the target resource.
- `RESOURCE_TYPE`: Type of the Kubernetes resource (deployment or statefulset).
- `RESOURCE_NAME`: Name of the Kubernetes resource (Deployment or StatefulSet).
- `BUCKET_NAME`: Name of the AWS S3 bucket for log storage.

## .env File Example

```command
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=your-region
NAMESPACE=database
RESOURCE_TYPE=deployment
RESOURCE_NAME=postgres
BUCKET_NAME=postgres-database-logs
```

## Local Setup

1. Clone the repository and navigate to the directory:

```command
git clone https://github.com/mercybassey/log-retriever-in-kubernetes
cd log-retriever-in-kubernetes
```

2. Install the required Python packages:

```command
pip install -r requirements.txt
```

3. Set up the .env file with the necessary environment variables.
4. Dockerize the script:

```command
docker build -t k8s-log-collector:latest .
```

## Kubernetes Deployment

### RBAC Configuration

Before deploying the script, set up the necessary RBAC permissions:

1. Create a ClusterRole:

Define a ClusterRole with the necessary permissions to access the required Kubernetes resources.

```command
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: log-collector-clusterrole
rules:
- apiGroups: ["apps"]
  resources: ["statefulsets", "deployments"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
```

Apply this configuration with `kubectl apply -f clusterrole.yaml`.

2. Create a ClusterRoleBinding:
Bind the ClusterRole to the service account that the script will use.

```command
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

Apply this configuration with kubectl apply -f clusterrolebinding.yaml.

## Deploy the CronJob

1. Create a Kubernetes Secret for AWS Credentials:

```command
kubectl create secret generic aws-credentials \
  --from-literal=aws_access_key_id=your-access-key-id \
  --from-literal=aws_secret_access_key=your-secret-access-key
```

2. Deploy the CronJob:

Create a Kubernetes manifest file and ensuring all environment variables are correctly set:

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
            image: [registry-username]/k8s-log-collector:latest
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
                value: "database"
              - name: RESOURCE_TYPE
                value: "deployment"  # or "statefulset"
              - name: RESOURCE_NAME
                value: "postgres"
              - name: BUCKET_NAME
                value: "postgres-database-logs"
          restartPolicy: OnFailure
```

Replace `[registry-username]/k8s-log-collector:latest` with your Docker image.

Save this manifest to a file, e.g., `log-collector-cronjob.yaml`, and deploy
the CronJob to your Kubernetes cluster with `kubectl apply -f log-collector-cronjob.yaml`.

## Notes

- `Schedule`: The schedule field is a cron expression that determines how often the job runs.
The example `*/30 * * * *` means the job will run every thirty minutes. You can adjust this to suit your needs.

- `Container Image`: Replace `[registry-username]/k8s-log-collector:latest` with the your Docker image.
- `Environment Variables`: The manifest sets environment variables from the Kubernetes secret `aws-credentials` for AWS credentials. Other environment - - variables are set directly. Make sure these values match your environment and use case.
- `Restart Policy`: The restartPolicy is set to OnFailure, meaning Kubernetes will restart the job if it fails.

## Deploying the CronJob

- Save this manifest to a file, e.g., `log-collector-cronjob.yaml`.
- Deploy the CronJob to your Kubernetes cluster:

```command
kubectl apply -f log-collector-cronjob.yaml
```

This will create a CronJob in your Kubernetes cluster that periodically runs the log collector script according to the specified schedule.
