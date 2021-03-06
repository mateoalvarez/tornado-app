from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import os
import logging
import requests

LOGGER = logging.getLogger(__name__)

AGGREGATED_KEY = "aggregated"
PYXIS_CLASSFICATION_KEY= "pyxis-classification"
_AGGREGATED = 0

class DispatcherApplication():

    def __init__(self, mongo_host=None, mongo_port=None, mongo_dbname="nonempty", mongo_collectionname="nonempty"):
        LOGGER.debug("Creating mongo client with - {ip}:{port}".format(ip=mongo_host, port=mongo_port))
        mongo_client = MongoClient(mongo_host, mongo_port)
        LOGGER.debug("Setting mongo database - {name}".format(name=mongo_dbname))
        mongo_database = mongo_client[str(mongo_dbname)]
        LOGGER.debug("Setting mongo collection - {name}".format(name=mongo_collectionname))
        # This operation is lazy, there will not render any error in case exists until an operation has been made
        self._mongo_collection = mongo_database[str(mongo_collectionname)]
        self.models = os.environ.get("MODELS")
        self.preprocessing = os.environ.get("PREPROCESSING")

    def get_kafka_consumer(self, kafka_topic=None, kafka_bootstrap_server=None):
        """
        This method return a KafkaConsumer configured to begin to retrieve information
        from configured bootstrap and topic
        :param kafka_topic:
        :param kafka_bootstrap_server:
        :return: A configured KafkaConsumer instance
        """
        if kafka_topic is None:
            LOGGER.critical("There is not present a required parameter kafka_topic")
            return None
        if kafka_bootstrap_server is None:
            LOGGER.critical("There is not present a required parameter kafka_bootstrap_server")
            return None
        consumer = KafkaConsumer(kafka_topic,
                                 bootstrap_servers=kafka_bootstrap_server,
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        LOGGER.info("A custom KafkaConsumer has been created with {topic} as topic and {server} as bootstrap_server".format(
            topic=kafka_topic, server=kafka_bootstrap_server))
        return consumer

    def get_data_preprocessed(self, data):
        LOGGER.info("Retrieved data will be preprocessed...")
        # here we should make a remote call,
        # instead and only for development purposes. We filter data inside the function
        # if data is None:
        #     return None
        # if "text" in data:
        #     return data["text"]
        # else:
        #     return None
        # data = "the gorgeously elaborate continuation of \" the lord of the rings \" trilogy is so huge that a column of words cannot adequately describe co-writer/director peter jackson's expanded vision of j . r . r . tolkien\'s middle-earth ."

        data = data.\
        replace("&", "&#38;").\
        replace("\'", "&#39;").\
        replace("\"", "&#34;").\
        replace("#", "&#35;")
        # template_url = "https://s3.eu-central-1.amazonaws.com/tornado-app/Templates/input_data_template.json"
        # input_data_json_template = json.loads(requests.get(template_url).content.decode('utf-8'))
        # input_data_json_template['rows'][0][0] = input_data_json_template['rows'][0][0].format(text=data)
        # data = json.dumps(input_data_json_template)

        # from pprint import pprint
        # print('\n\n\n\n\n')
        # pprint(input_data_json_template)
        # print('\n\n\n\n\n')
        # print(self.preprocessing)
        # print('\n\n\n\n\n')
        # print(data)
        # print('\n\n\n\n\n')

        first_request_template = json.dumps(
        {
          "schema": {
            "fields": [{
              "name": "label",
              "type": "double"
            },{
              "name": "features",
              "type": "string"
            }]
          },
          "rows": [[1.0, data]]
        })


        # print('\n\n\n\n')
        # print(first_request_template)
        # print('\n\n\n\n')

        response = []
        headers = {'Content-type': 'application/json'}
        for preprocessing_id in [self.preprocessing]:
            preprocessing_url = "http://prepr-" + str(preprocessing_id) + ":65327/transform"
            for i in range(0,10):
                while True:
                    try:
                        response.append(requests.post(\
                        preprocessing_url,\
                        data=first_request_template,\
                        headers=headers\
                        ).text)#["rows"][0][-1]
                    except Exception as e:
                        print('\n\n\n')
                        print('### Exception calling model service [times:{i}]###'.format(i=i))
                        print(e)
                        print('\n\n\n')
                        continue
                    break


        return response[0]

    def get_responses_from_models(self, data):
        """Request to models and return predictions"""
        import ast # To convert string to list
        # print('\n\n\n')
        # from pprint import pprint
        # pprint(data)
        # print('\n\n\n')
        second_request_template = json.dumps(
        {
          "schema": {
            "fields": [{
              "name": "label",
              "type": "double"
            },{
              "name": "features",
              "type": {
                "type": "tensor",
                "base": "double",
                "dimensions": [262144]
              }
            }]
          },
          "rows": [[1.0, data]]
        })

        # print('\n\n\n')
        # from pprint import pprint
        # print("Second")
        # pprint(second_request_template)
        # print('\n\n\n')

        response = []
        headers = {'Content-type': 'application/json'}
        for model_id in ast.literal_eval(self.models):
            model_url = "http://model-" + str(model_id) + ":65327/transform"
            for i in range(0,10):
                while True:
                    try:
                        response.append(float(json.loads(requests.post(\
                        model_url,\
                        data=second_request_template,\
                        headers=headers\
                        ).text)["rows"][0][-1]))
                    except Exception as e:
                        print('\n\n\n')
                        print('### Exception calling model service ###')
                        print(e)
                        print('\n\n\n')
                        continue
                    break

        # print('\n\n\n\n\n')
        # from pprint import pprint
        # print('RESPONSE')
        # pprint(response)
        # print('\n\n\n\n\n')
        return response

    def get_classification_value(self, model_values, classification_code=None):
        # set default 0
        tweet_classification = 0
        num_models = len(model_values)

        if classification_code:
            exec(classification_code)
        else:
            if num_models>1:
                tweet_classification = sum(model_values)/num_models
            else:
                tweet_classification = model_values[0]

        return round(tweet_classification)

    def get_true_classification(self, data, tweet):
        """True classification"""
        model_values = self.get_responses_from_models(data)
        tweet[PYXIS_CLASSFICATION_KEY] = self.get_classification_value(model_values=model_values)

        return tweet

    def get_fake_classification(self, data):
        data["malaas_application_value"] = "inserted_with_malaas"
        return data

    def store_in_mongo(self, data):
        LOGGER.info("Storing data in MongoDB")
        try:
            inserted_data_id = self._mongo_collection.insert_one(data).inserted_id
            LOGGER.info("Inserted data succesfully")
            if inserted_data_id is not None:
                return True
        except Exception as e:
            LOGGER.error("Something went wrong while data were being inserted into mongo database")
            LOGGER.error(e)
        return False

    def get_latest_aggregated_value(self):
        LOGGER.info("Restoring aggregated value from database")
        aggregated = 0;
        try:
            elements = list(self._mongo_collection.find().sort([("_id", -1)]).limit(1))
            if len(elements) == 0:
                aggregated = 0
            else:
                try:
                    # in case AGGREGATED_KEY is not present in stored data
                    aggregated = elements[0][AGGREGATED_KEY]
                except Exception as e:
                    aggregated = 0
        except Exception as e:
            LOGGER.error("Something went wrong while data were being inserted into mongo database")
            LOGGER.error(e)
        return round(aggregated)



def run_application():
    """
    Run application
    :return:
    """
    # check environment variables required to run
    kafka_topic = os.environ.get("KAFKA_TOPIC", "foobar_python")
    kafka_bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "127.0.0.1")

    # chek environment variable required to run with mongo
    # -e MONGODB_IP=192.168.240.3 -e MONGODB_PORT=27017 -e MONGODB_DBNAME=mycustomdb -e MONGODB_COLLECTIONNAME=cycustomcollection
    mongo_host = os.environ.get("MONGODB_HOST", "127.0.0.1")
    mongo_port = int(os.environ.get("MONGODB_PORT", "27017"))
    mongo_dbname = os.environ.get("MONGODB_DBNAME")
    mongo_collectionname = os.environ.get("MONGODB_COLLECTION_NAME")

    if kafka_topic is None:
        LOGGER.critical("There is not KAFKA_TOPIC present in environment")
        return None
    if kafka_bootstrap_server is None:
        LOGGER.critical("There is not KAFKA_BOOTSTRAP_SERVER present in environment")
        return None
    dispatcher_application = DispatcherApplication(mongo_host, mongo_port, mongo_dbname, mongo_collectionname)
    consumer = dispatcher_application.get_kafka_consumer(kafka_topic, kafka_bootstrap_server)

    _AGGREGATED = dispatcher_application.get_latest_aggregated_value()

    for msg in consumer:
        # msg is string type, it should be transformed to json and send to be preprocessed
        LOGGER.info(" Retrieved message from queue")
        LOGGER.info("  -> offset: {offset} ".format(offset=str(msg.offset)))
        LOGGER.info("  -> topic: {topic} ".format(topic=msg.offset))
        try:
            data_from_message = json.loads(msg.value)["full_text"]
        except Exception as exception:
            data_from_message = json.loads(msg.value)["text"]
        # print('\n\n\n\n')
        # print(data_from_message)
        # print('\n\n\n\n')
        try:
            text = dispatcher_application.get_data_preprocessed(data_from_message)
            # print(" # Retrieve data --> " + text)
            LOGGER.info(" Text extrated from data:")
            LOGGER.info("  -> text: {text} ".format(text=text))
            # from pprint import pprint
            # print('\n\n\n\n')
            # print('############data_from_message#########')
            # pprint(msg.value)
            # print('\n\n\n\n')
            data = dispatcher_application.get_true_classification(json.loads(text)["rows"][0][-1], tweet=json.loads(msg.value))
            # print('\n\n\n\n')
            # print('########')
            # from pprint import pprint
            # pprint(data)
            # print('\n\n\n\n')
            # make calling to models and generate json to be stored in mongo
            # data = dispatcher_application.get_fake_classification(data_from_message)

            _AGGREGATED = _AGGREGATED + data[PYXIS_CLASSFICATION_KEY]
            data[AGGREGATED_KEY] = _AGGREGATED

            # store data in mongo
            dispatcher_application.store_in_mongo(data)
            print('\n\n')
            print('INSERTED')

        except Exception as exception:
            print("############ ERROR ############")
            print(exception)
            print("############ ERROR ############")

if __name__ == '__main__':
    run_application()
