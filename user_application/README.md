# Deploy only using docker

## Requirements

### Deploy kafka
Note that you must know beforehand the IP that docker would set to your kafka container in order to set this IP to your user_application

```
docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=192.168.240.2 --env ADVERTISED_PORT=9092 spotify/kafka
```

### Deploy Mongo

Interesting links:
- https://www.mongodb.com/blog/post/running-mongodb-as-a-microservice-with-docker-and-kubernetes

Run Mongo docker container:

```
docker run --name some-mongo -d mongo
```


## Deploy exploiter_data_collector on docker
Genereate exploiter_data_collector docker images:

```
cd exploiter_data_collector
docker build -t exploiter-data-collector:0.1.0 .
```

Run docker container:
```
docker run --rm -e KAFKA_BOOTSTRAP_SERVER=192.168.240.2 -e KAFKA_TOPIC=mycustomtopic exploiter-data-collector:0.1.0
```

##  Deploy exploiter_core on docker
Genereate exploiter_core docker images:

```
cd exploiter_core
docker build -t exploiter-core:0.1.0 .
```

Run docker container:
```
docker run --rm -e KAFKA_BOOTSTRAP_SERVER=192.168.240.2 -e KAFKA_TOPIC=mycustomtopic -e MONGODB_IP=192.168.240.3 -e MONGODB_PORT=27017 -e MONGODB_DBNAME=mycustomdb -e MONGODB_COLLECTIONNAME=cycustomcollection exploiter-core:0.1.0
```


