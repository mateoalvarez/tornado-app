"""Main deployer"""
import os
import boto3
import kubernetes
import yaml
from pprint import pprint


BUCKET_DATASETS = os.environ.get("BUCKET_DATASET", "tornado-app-datasets")
BUCKET_DATASETS_REGION = os.environ.get("BUCKET_DATASETS_REGION", "eu-central-1")
BUCKET_SPARK_JOBS = os.environ.get("BUCKET_SPARK_JOBS", "tornado-app-emr")
BUCKET_SPARK_JOBS_REGION = os.environ.get("BUCKET_SPARK_JOBS_REGION", "eu-central-1")
BUCKET_K8S_TEMPLATES = os.environ.get("BUCKET_K8S_TEMPLATES", "tornado-app-k8s-templates")
NAMESPACE = 'default'
# CLUSTER_KEY = os.environ.get("CLUSTER_KEY", "YkKxAqtfOH13QuwcHvDunsoOjaYGljNF")

CONFIGURATION = kubernetes.client.Configuration()
# CONFIGURATION.api_key['authorization'] =

class MainDeployer():
    """Deploy all containers on kubernetes"""

    def __init__(self, BUCKET_DATASETS_REGION, CONFIGURATION):
        self.S3_CLIENT = boto3.client("s3", region_name=BUCKET_DATASETS_REGION)
        self.S3_RESOURCE = boto3.resource("s3", region_name=BUCKET_DATASETS_REGION)
        self.KUBERNETES_V1 = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(CONFIGURATION))
        self.KUBERNETES_DEPLOYMENT = kubernetes.client.ExtensionsV1beta1Api(kubernetes.client.ApiClient(CONFIGURATION))
        self.NAMESPACE = 'default'

    def deploy_kafka_producer(self):
        """Deploy producer on cluster"""
        self.S3_RESOURCE.meta.client.download_file(BUCKET_K8S_TEMPLATES, 'kafka-producer-service.yaml', '/tmp/kafka-producer-service.yaml')
        self.S3_RESOURCE.meta.client.download_file(BUCKET_K8S_TEMPLATES, 'kafka-producer-deployment.yaml', '/tmp/kafka-producer-deployment.yaml')
        # prereq_file = requests.get(\
        # "https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/prereq_template_job_file.sh")\
        # .content.decode('utf-8').format(job_file=job_file_url)
        # kafka_producer_service = yaml.load(open('/Users/Mat/github/tornado-app/user_application/k8s_deployment/yaml_templates/kafka_server/kafka_server_service.yaml').read())
        kafka_producer_service = yaml.load(open('/tmp/kafka-producer-service.yaml').read())
        kafka_producer_deployment = yaml.load(open('/tmp/kafka-producer-deployment.yaml').read())
        try:
            api_response = self.KUBERNETES_V1.create_namespaced_service(self.NAMESPACE, body=kafka_producer_service, pretty=True)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)
        try:
            api_response = self.KUBERNETES_DEPLOYMENT.create_namespaced_deployment(self.NAMESPACE, body=kafka_producer_deployment, pretty=True)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)


    def deploy_model(self):
        """Deploy model on cluster"""
        pass

    def deploy_preprocessing(self):
        """Deploy preprocessing on cluster"""
        pass
