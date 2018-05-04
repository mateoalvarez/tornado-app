# Pyxis Customization MLeap-Serving docker image

- Generate Pyxis Mleap-Serving docker image based on: https://github.com/combust/mleap/tree/master/mleap-serving

``` bash
docker build -t custom-mleap:0.1.0 .
```

- Execute Pyxis Mleap-Serving docker image. Note that you probably need to change ip that will be used to retrieve model.

``` bash
docker run --rm -p 65327:65327 --name pyxis-mleap -e MODEL_URL="http://10.244.67.174:8000/airbnb.model.lr.zip" custom-mleap:0.1.0
```

- Test Pyxis Mleap-Serving docker image.

``` bash
curl -XGET -H "content-type: application/json" http://192.168.240.2:65327/model
```

- Get predictions

``` bash
curl -XPOST -H "accept: application/json" -H "content-type: application/json" -d @/tmp/models/frame.airbnb.json http://192.168.240.2:65327/transform
```

- Stop Pyxis container:

``` bash
docker rm -f pyxis-mleap
```
