CREATE DATABASE twitter_app_db;
\connect twitter_app_db
CREATE TYPE application_status_enum AS ENUM ('running', 'stopped', 'error');
CREATE TYPE pipeline_status_enum AS ENUM ('untrained', 'training', 'trained', 'error');
CREATE TYPE code_block_type AS ENUM ('input', 'output', 'preprocessing', 'model');

CREATE TABLE users (
  id SERIAL UNIQUE,
  email VARCHAR,
  hashed_password VARCHAR,
  name VARCHAR(20),
  type INTEGER,
  creation_date DATE NOT NULL DEFAULT(now()),
  last_login DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, email)
);

-- Access data for twitter
CREATE TABLE datasource_settings (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  type INTEGER NOT NULL DEFAULT(1),
  datasource_access_settings JSONB,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE datasets (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  dataset_name VARCHAR NOT NULL,
  storage_url VARCHAR NOT NULL,
  dataset_description TEXT,
  dataset_properties JSONB, -- {columns:# , rows:# , labels:# }
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE engines (
  id SERIAL UNIQUE,
  engine_name VARCHAR(20),
  engine_configuration JSONB,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id)
);

-- Templates for models

CREATE TABLE code_block_templates (
  id  SERIAL UNIQUE,
  template_name VARCHAR(20),
  model_engine INTEGER NOT NULL DEFAULT(1),
  description TEXT,
  type code_block_type,
  code_content JSONB,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id),
  FOREIGN KEY (model_engine) REFERENCES engines(id)
);

-- Block codes for users

CREATE TABLE code_block (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  code_block_template_id INTEGER NOT NULL,
  code_content JSONB,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (code_block_template_id) REFERENCES code_block_templates(id)
);

CREATE TABLE classification_criteria (
  id SERIAL UNIQUE,
  name VARCHAR(20),
  properties JSONB,
  description TEXT,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id)
);

-- Twitter configuration

-- Configuration:
-- datasource_application_config: {
--  keywords:
-- }
CREATE TABLE datasource_configurations (
  id SERIAL UNIQUE,
  datasource_settings_id INTEGER NOT NULL,
  datasource_application_config JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id)
);
-- pipeline_files
-- pipeline_files: {
--   model_files: [{model_name: model_link}, {model_name: model_link}],
--   preprocessing_files: [{preprocessing_name: preprocessing_link}],
--   metric_files: metric_files_link
-- }

CREATE TABLE pipelines (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  pipeline_name VARCHAR(20),
  training_config_resources JSONB,
  pipeline_dataset INTEGER NOT NULL,
  classification_criteria INTEGER NOT NULL,
  pipeline_status pipeline_status_enum,
  pipeline_prep_stages_ids INTEGER ARRAY NOT NULL,
  pipeline_models_ids INTEGER ARRAY NOT NULL,
  pipeline_files JSONB,
  error_status TEXT,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (pipeline_dataset) REFERENCES datasets(id),
  FOREIGN KEY (classification_criteria) REFERENCES classification_criteria(id)
);

CREATE TABLE  applications (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  application_name VARCHAR(20),
  application_pipeline INTEGER NOT NULL,
  application_status application_status_enum,
  datasource_configuration_id INTEGER,
  datasource_settings_id INTEGER,
  artifacts_download_url JSONB,
  creation_date DATE NOT NULL DEFAULT(now()),
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (application_pipeline) REFERENCES pipelines(id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id),
  FOREIGN KEY (datasource_configuration_id) REFERENCES datasource_configurations(id)
);



-- INSERT EXAMPLE code_block_templates
-- FIRST USER ADMIN
INSERT INTO users(email, hashed_password, name, type)
VALUES ('admin@pyxisml.com','$2b$12$jzfu7DwswPSzBWV9tjHSpeBxuasg27M9Ho5Zw7yKPBekmCNm.F8OS','ADMIN',1);
-- TWITTER API FOR ADMIN
INSERT INTO datasource_settings (user_id, type, datasource_access_settings)
VALUES (1, 1, '{"TWITTER_CONSUMER_API_KEY":"qUBED8JONS1rdOXMGXxJw3KDK", "TWITTER_CONSUMER_API_SECRET":"DUI0ICvIXTYE4SPxdBSRVlq3xEw1UDpcy6mZG2qWE1yyX3nH2M", "TWITTER_CONSUMER_TOKEN":"245605482-rajqw4klordPOid8izXvAHBc8DhU8QliOFraCFqM", "TWITTER_CONSUMER_SECRET":"kYalUO9SmnLvcjXPIrRE0dSEDd2LhQBSBMPD57UgLvzse"}');
-- CLASSIFICATION CRITERIA
INSERT INTO classification_criteria (name, properties, description)
VALUES ('Default', '{}', 'Votación en caso de ser número impar de modelos. En caso de ser par, máxima probabilidad');
-- ENGINE
INSERT INTO engines (engine_name,engine_configuration)
VALUES ('spark', '{}');
-- MODELS
INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('initializer', 1, 'input', '{"code": "import nltk\nimport random\nfrom nltk.corpus import movie_reviews\nfrom nltk.classify.scikitlearn import SklearnClassifier\nfrom nltk.tokenize import word_tokenize\nimport pyspark\nfrom pyspark.sql import SparkSession\nspark = SparkSession.builder.appName(\"Basic template\").config(\"spark.jars.packages\",\"ml.combust.mleap:mleap-spark-base_2.11:0.7.0,ml.combust.mleap:mleap-spark_2.11:0.7.0\").getOrCreate()\nsc = spark.sparkContext\ninput_data = sc.textFile(\"<dataset>\").map(lambda line: line.split(\"\t\"))\nfrom pyspark import Row\ninput_data_splitted = input_data.map(lambda line: Row(features=line[0], label=int(float(line[1]))))\nfrom pyspark.sql.types import StringType, IntegerType\nfrom pyspark.sql.types import *\nschema = StructType([StructField(\"label\", IntegerType(), False), StructField(\"features\", StringType(), False)])\ninput_data_df = spark.createDataFrame(input_data_splitted, schema=schema)\npipeline_preprocessing_stages = []\npipeline_models_stages = []\npipeline_stages = []\n", "params":"[<dataset>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('pos_tagger', 1, 'preprocessing', '{"code": "from pyspark.ml.param.shared import HasInputCol, HasOutputCol, HasNumFeatures\nfrom pyspark import keyword_only\nfrom pyspark.ml.wrapper import JavaTransformer\nfrom pyspark.mllib.common import inherit_doc\n\n\n@inherit_doc\nclass PosTaggerCoreNLPSparkTransformer(JavaTransformer, HasInputCol, HasOutputCol):\n\n\t@keyword_only\n\tdef __init__(self, inputCol=\"input\", outputCol=\"output\"):\n\t\tsuper(PosTaggerCoreNLPSparkTransformer, self).__init__()\n\t\tself._pos_tagger_java_model = self._new_java_obj(\"ml.combust.mleap.core.feature.PosTaggerCoreNLPModel\", \"<language>\", \"<tags>\")\n\t\tself._java_obj = self._new_java_obj(\"org.apache.spark.ml.mleap.feature.PosTaggerCoreNLPSparkTransformer\", self.uid, self._pos_tagger_java_model)\n\t\tkwargs = self._input_kwargs\n\t\tself.setParams(**kwargs)\n\n\t@keyword_only\n\tdef setParams(self, inputCol=\"input\", outputCol=\"output\"):\n\t\tkwargs = self._input_kwargs\n\t\treturn self._set(**kwargs)\n\nCORENLP_POS_TAGGER = PosTaggerCoreNLPSparkTransformer(inputCol=\"features\", outputCol=\"corenlp_pos_tagger_col\")\npipeline_preprocessing_stages.append(CORENLP_POS_TAGGER)", "params":"[<language>,<tags>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('tokenizer', 1, 'preprocessing', '{"code": "from pyspark.ml.feature import Tokenizer\nif (bool(pipeline_preprocessing_stages)):\n\tTOKENIZER = Tokenizer(inputCol=pipeline_preprocessing_stages[-1].getOutputCol(), outputCol=\"tokenizer_col\")\nelse:\n\tTOKENIZER = Tokenizer(inputCol=\"features\", outputCol=\"tokenizer_col\")\npipeline_preprocessing_stages.append(TOKENIZER)\n", "params":"[]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('hashingtf', 1, 'preprocessing', '{"code": "from pyspark.ml.feature import HashingTF\nif (bool(pipeline_preprocessing_stages)):\n\tHASHINGTF = HashingTF(inputCol=pipeline_preprocessing_stages[-1].getOutputCol(), outputCol=\"hashingtf_col\")\nelse:\n\tHASHINGTF = HashingTF(inputCol=\"features\", outputCol=\"hashingtf_col\")\npipeline_preprocessing_stages.append(HASHINGTF)\n", "params":"[]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('logistic_regression', 1, 'model', '{"code": "from pyspark.ml.classification import LogisticRegression\nlr = LogisticRegression(maxIter=10, regParam=0.001)\npipeline_models_stages.append((lr.uid, lr))\n", "params":"[<lr_max_iter>,<lr_reg_param>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('naive_bayes', 1, 'model', '{"code": "from pyspark.ml.classification import NaiveBayes\nnb = NaiveBayes(smoothing=1.0, modelType="multinomial")\npipeline_models_stages.append((nb.uid, nb))\n", "params":"[<smoothing>,<modelType>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('lineal_svm', 1, 'model', '{"code": "from from pyspark.ml.classification import LinearSVC\nlsvc = LinearSVC(maxIter=10, regParam=0.1)\npipeline_models_stages.append((lsvc.uid, lsvc))\n", "params":"[<maxIter>,<regParam>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('decision_tree', 1, 'model', '{"code": "from from pyspark.ml.classification import DecisionTreeClassifier\ndt = DecisionTreeClassifier(maxDepth=3, labelCol="label")\npipeline_models_stages.append((dt.uid, dt))\n", "params":"[<maxDepth>,<labelCol>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('pipeline_execution', 1, 'output', '{"code": "from pyspark.ml import Pipeline, PipelineModel\nlast_column_name = pipeline_preprocessing_stages[-1].getOutputCol()\npreprocessing_pipeline = Pipeline(stages=pipeline_preprocessing_stages)\npreprocessing_pipeline_trained = preprocessing_pipeline.fit(input_data_df).transform(input_data_df)\nmid_point = preprocessing_pipeline_trained\nfor stage in pipeline_preprocessing_stages[:-1]:\n\tpreprocessing_pipeline_trained = preprocessing_pipeline_trained.drop(stage.getOutputCol())\npreprocessing_pipeline_trained = preprocessing_pipeline_trained.drop(\"features\").withColumnRenamed(last_column_name, \"features\")\nmodels_pipelines = []\nfor model_name, model_pipeline in pipeline_models_stages:\n\tmodels_pipelines.append((model_name, model_pipeline.fit(preprocessing_pipeline_trained)))\n", "params":"[]"}');

-- INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
-- VALUES ('output', 1, 'output', '{"code": "from mleap import pyspark\nfrom mleap.pyspark.spark_support import SimpleSparkSerializer\npreprocessing_pipeline_serializable = preprocessing_pipeline.fit(input_data_df)\npreprocessing_pipeline_serializable.serializeToBundle(\"jar:file:s3:/tornado-app-emr/{user_email}/models/{application_id}/preprocessing.zip\", dataset=mid_point)\nfor model_name, model_pipeline in models_pipelines:\n\toutput_sample = model_pipeline.transform(preprocessing_pipeline_trained)\n\tmodel_pipeline.serializeToBundle(\"jar:file:s3:/tornado-app-emr/{user_email}/models/{application_id}/{model_name}.zip\".format(model_name=model_name), output_sample)\n", "params":"[]"}');

-- OUTPUT TO LOCAL AND THEN COPY TO S3
INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('output', 1, 'output', '{"code": "from mleap import pyspark\nfrom mleap.pyspark.spark_support import SimpleSparkSerializer\npreprocessing_pipeline_serializable = preprocessing_pipeline.fit(input_data_df)\npreprocessing_pipeline_serializable.serializeToBundle(\"jar:file:/tmp/models/preprocessing.zip\", dataset=mid_point)\nfor model_name, model_pipeline in models_pipelines:\n\toutput_sample = model_pipeline.transform(preprocessing_pipeline_trained)\n\tmodel_pipeline.serializeToBundle(\"jar:file:/tmp/models/{model_name}.zip\".format(model_name=model_name), output_sample)\n", "params":"[]"}');
