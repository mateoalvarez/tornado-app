# tornado-app

Tornado web app with postgresql database to launch tensorflow pipelines

## Setup
To setup the project,

Generate folder to store dev logs in order to be able to deploy the app
``` bash
mkdir src/app/logs
```

Make sure you have installed the required libraries.
``` bash
pip install -r setup/requirements.txt
```

Deploy postgres and make sure you have created the database in postgres.
``` bash
# deploy postgres container
docker run --name postgres -p 32769:5432 -v $(pwd)/src/db/create_database.sql:/create_database.sql -e POSTGRES_PASSWORD=mysecretpassword -d postgres

# connect to postgres container
docker exec -it $(docker ps -aqf "name=postgres") bash

# inside docker
# as postres user
psql
\i /create_database.sql
```

deploy the application on localhost, on port 8888
```bash
export AWS_ACCESS_KEY_ID=<AWS ID>
export AWS_SECRET_ACCESS_KEY=<AWS SECRET>
export BUCKET_DATASET=<DATASETS_BUCKET_NAME>
export BUCKET_DATASETS_REGION=<DATASETS_BUCKET_REGION>
python src/app/app.py
```

generate a docker image

```
cd tornado-app
docker build -t image:0.1.1 .
```

deploy docker image, by default it will use region=eu-west-1. In case you want to change it, you should set an extra environment variable: -e AWS_REGION=<your_region>

```
docker run -it --rm -p 9090:8888 -e DATABASE_NAME=twitter_app_db -e DATABASE_USER=postgres -e DATABASE_PASS=mysecretpassword -e DATABASE_HOST=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' postgres) -e DATABASE_PORT=5432  -e AWS_ACCESS_KEY_ID=<aws_access_key_id> -e AWS_SECRET_ACCESS_KEY=<aws_secret_access_key> -e BUCKET_DATASET=<bucket_dataset> -e BUCKET_DATASETS_REGION=<bucket_datasets_region> --name tornado-app image:0.1.1
```

# Tags used for POS Tagger stage

PosTagger feature is powered by [StanfordCoreNLP](https://stanfordnlp.github.io/CoreNLP/pos.html) library.

## Spanish Tag list
The tag set can be read [here](https://nlp.stanford.edu/software/spanish-faq.shtml#tagset)

## English Tag list
The tag set can be read [here](https://catalog.ldc.upenn.edu/docs/LDC99T42/tagguid1.pdf)

## Generate common tags names

In order to avoid to users know each tag of each language. In order to do that we have defined some tags groups:


### Spanish
Map for spanish tags:

```json
{
    "adjectives": ["ao0000", "aq0000"],
    "conjunctions": ["cc", "cs"],
    "determiners": ["da0000","dd0000","de0000","di0000","dn0000","do0000","dp0000","dt0000"],
    "punctuation": ["f0","faa","fat","fc","fca","fct","fd","fe","fg","fh","fia","fit","fp","fpa","fpt","fra","frc","fs","ft","fx","fz"],
    "interjections": ["i"],
    "nouns": ["nc00000","nc0n000","nc0p000","nc0s000","np00000"],
    "pronouns":["p0000000","pd000000","pe000000","pi000000","pn000000","pp000000","pr000000","pt000000","px000000"],
    "adverbs": ["rg","rn"],   
    "prepositions": ["sp000"],
    "verbs": ["va00000","vag0000","vaic000","vaif000","vaii000","vaip000","vais000","vam0000","van0000","vap0000","vasi000","vasp000","vmg0000","vmic000","vmif000","vmii000","vmip000","vmis000","vmm0000","vmn0000","vmp0000","vmsi000","vmsp000","vsg0000","vsic000","vsif000","vsii000","vsip000","vsis000","vsm0000","vsn0000","vsp0000","vssf000","vssi000","vssp000"],    
    "dates": ["w"],
    "numerals": ["z0","zm","zu"],
    "other": ["word"]
}
```

### English
Map for english tags:


```json
{
    "adjectives": ["JJ", "JJR", "JJS"],
    "conjunctions": ["CC"],
    "determiners": ["DT", "WDT", "PDT"],
    "punctuation": [],
    "interjections": ["UH"],
    "nouns": ["NN","NNS", "NNP", "NNPS"],
    "pronouns":["PRP","PRP$", "WP", "WP$"],
    "adverbs": ["RB","RBR", "RBS", "WRB"],   
    "prepositions": ["IN", "TO", "RP"],
    "verbs": ["EX","MD", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],    
    "dates": [],
    "numerals": ["CD"],
    "other": ["FW", "LS", "POS", "SYM"]
}
```
