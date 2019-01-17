"""Deployer for dispatcher"""
import kubernetes
import yaml
import requests
import logging

LOGGER = logging.getLogger(__name__)

class DispatcherDeployer():
    """Class to launch dispatcher of application"""

    def __init__(self, k8s_config, k8s_namespace, BUCKET_YAML_TEMPLATES, BUCKET_YAML_TEMPLATES_REGION):
        """Initializer"""

        self.delete_body = kubernetes.client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5)
        self.k8s_config_map = kubernetes.client.CoreV1Api(
            kubernetes.client.ApiClient(k8s_config))
        self.k8s_service = kubernetes.client.CoreV1Api(
            kubernetes.client.ApiClient(k8s_config))
        self.k8s_deployment = kubernetes.client.ExtensionsV1beta1Api(
            kubernetes.client.ApiClient(k8s_config))
        self.k8s_namespace = k8s_namespace
        self.BUCKET_YAML_TEMPLATES = BUCKET_YAML_TEMPLATES
        self.BUCKET_YAML_TEMPLATES_REGION = BUCKET_YAML_TEMPLATES_REGION

    def deploy_dispatcher(self, **kwargs):
        """Disparcher deployer"""

        dispatcher_config_map_template = requests.get(
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"
            + self.BUCKET_YAML_TEMPLATES
            + "/dispatcher/dispatcher_config_map.yaml")\
            .content.decode("utf-8").format(
                application_id=kwargs["application_id"],
                application_models=kwargs["pipeline_models_ids"],
                application_preprocessing=kwargs["id"],
                application_classification_configuration=kwargs["classification_configuration"])

        dispatcher_template = requests.get(
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"
            + self.BUCKET_YAML_TEMPLATES+"/dispatcher/dispatcher_deployment.yaml")\
            .content.decode("utf-8").format(
                application_id=kwargs["application_id"],
                MONGODB_DBNAME='user_' + str(kwargs["user_id"]),
                MONGODB_COLLECTION_NAME='application_' + kwargs["application_id"],
                KAFKA_TOPIC='application_' + kwargs["application_id"])

        try:
            self.k8s_config_map.create_namespaced_config_map(
                namespace=self.k8s_namespace,
                body=yaml.load(dispatcher_config_map_template),
                pretty=True)
        except Exception as exception:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % exception)

        try:
            self.k8s_deployment.create_namespaced_deployment(
                namespace=self.k8s_namespace,
                body=yaml.load(dispatcher_template),
                pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)

    def deploy_kafka_producer(self, application_id, keywords, datasource_settings, kafka_topic):
        """Kafka producer deployer"""
        print("## -> begin deploy_kafka_producer arguments")
        print("\tapplication_id -> {app_id}".format(app_id=application_id))
        print("\tkeywords -> {keywords}".format(keywords=keywords))
        print("\tdatasource_settings -> {datasource_settings}".format(datasource_settings=str(datasource_settings)))
        print("\tkafka_topic -> {kafka_topic}".format(kafka_topic=kafka_topic))
        print("## <- end deploy_kafka_producer arguments")

        LOGGER.info("## -> begin deploy_kafka_producer arguments")
        LOGGER.info("\tapplication_id -> {app_id}".format(app_id=application_id))
        LOGGER.info("\tkeywords -> {keywords}".format(keywords=keywords))
        LOGGER.info("\tdatasource_settings -> {datasource_settings}".format(datasource_settings=str(datasource_settings)))
        LOGGER.info("\tkafka_topic -> {kafka_topic}".format(kafka_topic=kafka_topic))
        LOGGER.info("## <- end deploy_kafka_producer arguments")


        producer_template = requests.get(
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"
            + self.BUCKET_YAML_TEMPLATES
            + "/dispatcher/kafka_producer_deployment.yaml")\
            .content.decode("utf-8").format(
                application_id=application_id,
                WORDS_TO_TRACK=keywords,
                KAFKA_TOPIC=kafka_topic,
                TWITTER_API_KEY=datasource_settings["TWITTER_API_KEY"],
                TWITTER_API_SECRET_KEY=datasource_settings["TWITTER_API_SECRET_KEY"],
                TWITTER_ACCESS_TOKEN=datasource_settings["TWITTER_ACCESS_TOKEN"],
                TWITTER_ACCESS_TOKEN_SECRET=datasource_settings["TWITTER_ACCESS_TOKEN_SECRET"])

        try:
            self.k8s_deployment.create_namespaced_deployment(
                namespace=self.k8s_namespace,
                body=yaml.load(producer_template),
                pretty=True)
        except Exception as e:
            print("Exception when calling AppsV1Api->create_namespaced_replica_set: %s\n" % e)
            LOGGER.error("Exception in kafka producer deployment process")
            LOGGER.error(str(e))


    def deploy_models(self, pipeline_id, model_ids, model_urls):
        """Deploy all application's models"""

        deploy_template = requests.get(
            "https://s3." + self.BUCKET_YAML_TEMPLATES_REGION
            + ".amazonaws.com/" + self.BUCKET_YAML_TEMPLATES
            + "/mleap/model_deployment.yaml")\
            .content.decode("utf-8")

        service_template = requests.get(
            "https://s3." + self.BUCKET_YAML_TEMPLATES_REGION
            + ".amazonaws.com/" + self.BUCKET_YAML_TEMPLATES
            + "/mleap/model_service.yaml")\
            .content.decode("utf-8")

        model_deployment_templates = []
        model_service_templates = []

        for model_id, model_url in zip(model_ids, model_urls):
            model_deployment_templates.append(
                deploy_template.format(
                    model_id=model_id,
                    pipeline_id=pipeline_id,
                    model_url=model_url)
                )
            model_service_templates.append(
                service_template.format(
                    model_id=model_id,
                    pipeline_id=pipeline_id)
                )

        for model_template, model_service in zip(
                model_deployment_templates, model_service_templates):
            # deployment
            try:
                self.k8s_deployment.create_namespaced_deployment(
                    namespace=self.k8s_namespace,
                    body=yaml.load(model_template),
                    pretty=True)
            except Exception as e:
                print("Exception when calling V1Api->create_namespaced_deployment:%s\n" % e)
                LOGGER.error("Exception when calling V1Api->create_namespaced_deployment:%s\n" % e)
            # service
            try:
                self.k8s_service.create_namespaced_service(
                    namespace=self.k8s_namespace,
                    body=yaml.load(model_service),
                    pretty=True)
            except Exception as e:
                print("Exception when calling V1Api->create_service:%s\n" % e)
                LOGGER.error("Exception when calling V1Api->create_service:%s\n" % e)

    def deploy_preprocessing(self, pipeline_id, preprocessing_ids, preprocessing_url):
        """Deploy preprocessing stages"""

        deploy_template = requests.get(
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"
            + self.BUCKET_YAML_TEMPLATES
            + "/mleap/preprocessing_deployment.yaml")\
            .content.decode("utf-8")
        service_template = requests.get(
            "https://s3."+self.BUCKET_YAML_TEMPLATES_REGION+".amazonaws.com/"
            + self.BUCKET_YAML_TEMPLATES+"/mleap/preprocessing_service.yaml")\
            .content.decode("utf-8")

        prep_deployment_templates = []
        prep_service_templates = []
        # For now, just one preprocessing per application
        prep_deployment_templates.append(deploy_template.format(
            pipeline_id=pipeline_id,
            preprocessing_id=pipeline_id,
            preprocessing_url=preprocessing_url))

        prep_service_templates.append(service_template.format(
            pipeline_id=pipeline_id,
            preprocessing_id=pipeline_id))

        for prep_deployment, prep_service in zip(
                prep_deployment_templates, prep_service_templates):
            # deployment
            try:
                self.k8s_deployment.create_namespaced_deployment(
                    namespace=self.k8s_namespace,
                    body=yaml.load(prep_deployment),
                    pretty=True)
            except Exception as e:
                LOGGER.error("Exception when calling V1Api->create_namespaced_deployment:%s\n" % e)

            # service
            try:
                self.k8s_service.create_namespaced_service(
                    namespace=self.k8s_namespace,
                    body=yaml.load(prep_service),
                    pretty=True)
            except Exception as e:
                LOGGER.error("Exception when calling V1Api->create_service:%s\n" % e)

    def delete_deployments(self, application_id, pipeline_id, preprocessing_ids, model_ids):
        """DELETE kubernetes deployment"""

        application_deployment_name = 'dispatcher-' + str(application_id)
        # DEPLOYMENTS
        try:
            self.k8s_deployment.delete_namespaced_deployment(
                namespace=self.k8s_namespace,
                name=application_deployment_name,
                body=self.delete_body
                )

            # for preprocessing_id in preprocessing_ids:
            preprocessing_deployment_name = 'prepr-' + str(pipeline_id)
            self.k8s_deployment.delete_namespaced_deployment(
                namespace=self.k8s_namespace,
                name=preprocessing_deployment_name,
                body=self.delete_body
                )
            self.k8s_service.delete_namespaced_service(
                namespace=self.k8s_namespace,
                name=preprocessing_deployment_name,
                body=self.delete_body
                )

            for model_id in model_ids:
                model_name = 'model-' + str(model_id)
                self.k8s_deployment.delete_namespaced_deployment(
                    namespace=self.k8s_namespace,
                    name=model_name,
                    body=self.delete_body
                    )
                self.k8s_service.delete_namespaced_service(
                    namespace=self.k8s_namespace,
                    name=model_name,
                    body=self.delete_body
                    )

            kafka_producer_name = 'kafka-producer-' + str(application_id)
            self.k8s_deployment.delete_namespaced_deployment(
                namespace=self.k8s_namespace,
                name=kafka_producer_name,
                body=self.delete_body
                )

            dispatcher_config_map_name = "application-" + str(application_id) + "-configmap"
            self.k8s_config_map.delete_namespaced_config_map(
                namespace=self.k8s_namespace,
                name=dispatcher_config_map_name,
                body=self.delete_body
                )
        except kubernetes.client.rest.ApiException as exception:
            print("### Error Deleting deployment ###")
            print(exception)
            LOGGER.error("### Error Deleting deployment ###")
            LOGGER.error(exception)
        return
