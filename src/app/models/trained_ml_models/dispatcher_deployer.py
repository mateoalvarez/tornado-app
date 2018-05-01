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

    def deploy_dispatcher(self, application_id, user_id, datasource_configuration):
        """Disparcher deployer"""

        dispatcher_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/dispatcher_deployment.yaml").content.decode("utf-8").format(application_id=application_id, MONGODB_DBNAME='user_' + str(user_id), MONGODB_COLLECTION_NAME = 'application_' + str(application_id), KAFKA_TOPIC = 'application_' + str(application_id))

        try:
            self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(dispatcher_template), pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)

    def deploy_kafka_producer(self, application_id, keywords):
        """Kafka producer deployer"""

        producer_template = requests.get(\
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/kafka_producer_deployment.yaml").content.decode("utf-8").format(application_id=application_id, WORDS_TO_TRACK=keywords, KAFKA_TOPIC = 'application_' + str(application_id))

        try:
            self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(producer_template), pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)

    def deploy_models(self, application):
        """Deploy all application's models"""

        model_ids = application["application_models_ids"]
        deploy_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/model_deployment.yaml").content.decode("utf-8").format(application_id=application["id"]\
        )
        service_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/model_service.yaml").content.decode("utf-8").format(application_id=application["id"]\
        )

        model_deployment_templates = []
        model_service_templates = []

        for model_id in model_ids:
            model_deployment_templates.append(deploy_template.format(model_id=model_id))
            model_service_templates.append(service_template.format(model_id=model_id))

        for model_template, model_service in zip(model_deployment_templates, model_service_templates):
            # deployment
            try:
                self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(model_template), pretty=True)
            except Exception as e:
                print("Exception when calling V1Api->create_namespaced_deployment:%s\n" % e)
            # service
            try:
                self.k8s_service.create_namespaced_service(namespace=self.k8s_namespace, body=yaml.load(model_service), pretty=True)
            except Exception as e:
                print("Exception when calling V1Api->create_service:%s\n" % e)


    def deploy_preprocessing(self, application):
        """Deploy preprocessing stages"""
        preprocessing_id = application["application_prep_stages_ids"]

        deploy_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/preprocessing_deployment.yaml").content.decode("utf-8").format(application_id=application["id"], preprocessing_id=preprocessing_id\
        )
        service_template = requests.get(\
        "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"+self.BUCKET_YAML_TEMPLATES+"/dispatcher/preprocessing_service.yaml").content.decode("utf-8").format(application_id=application["id"], preprocessing_id=preprocessing_id\
        )

        # deployment
        try:
            self.k8s_deployment.create_namespaced_deployment(namespace=self.k8s_namespace, body=yaml.load(deploy_template), pretty=True)
        except Exception as e:
            print("Exception when calling V1Api->create_namespaced_deployment:%s\n" % e)

        # service
        try:
            self.k8s_service.create_namespaced_service(namespace=self.k8s_namespace, body=yaml.load(service_template), pretty=True)
        except Exception as e:
            print("Exception when calling V1Api->create_service:%s\n" % e)
