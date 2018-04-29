"""Deployer for dispatcher"""
import os
import kubernetes
import yaml
import requests

class DispatcherDeployer():
    """Class to launch dispatcher of application"""

    def __init__(self, k8s_config, k8s_namespace, BUCKET_YAML_TEMPLATES, BUCKET_YAML_TEMPLATES_REGION):
        """Initializer"""

        self.k8s_config_map = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(k8s_config))
        self.k8s_service = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(k8s_config))
        self.k8s_deployment = kubernetes.client.ExtensionsV1beta1Api(kubernetes.client.ApiClient(k8s_config))
        self.k8s_namespace = k8s_namespace
        self.BUCKET_YAML_TEMPLATES = BUCKET_YAML_TEMPLATES
        self.BUCKET_YAML_TEMPLATES_REGION = BUCKET_YAML_TEMPLATES_REGION

    def deploy_dispatcher(self, application):
        """Disparcher deployer"""

        dispatcher_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/dispatcher_deployment.yaml").content.decode("utf-8").format(application_id=application["id"])

        try:
            self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(dispatcher_template), pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)

    def deploy_kafka_producer(self, application):
        """Kafka producer deployer"""

        producer_template = requests.get(\
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/kafka_producer_deployment.yaml").content.decode("utf-8").format(application_id=application["id"])

        try:
            self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(producer_template), pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)
