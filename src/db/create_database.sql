CREATE DATABASE twitter_app_db;
CREATE TYPE application_status_enum AS ENUM ('untrained', 'training', 'trained', 'running', 'stopped', 'error');
CREATE TYPE code_block_type AS ENUM ('input', 'output', 'preprocessing', 'model');
\connect twitter_app_db

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
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE engines (
  id SERIAL UNIQUE,
  engine_name VARCHAR(20),
  engine_configuration JSONB,
  PRIMARY KEY (id)
);

-- Templates for models

CREATE TABLE code_block_templates (
  id  SERIAL UNIQUE,
  template_name VARCHAR(20),
  model_engine INTEGER NOT NULL DEFAULT(1),
  type code_block_type,
  code_content JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (model_engine) REFERENCES engines(id)
);

-- Block codes for users

CREATE TABLE code_block (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  code_block_template_id INTEGER NOT NULL,
  code_content JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (code_block_template_id) REFERENCES code_block_templates(id)
);

CREATE TABLE classification_criteria (
  id SERIAL UNIQUE,
  name VARCHAR(20),
  properties JSONB,
  PRIMARY KEY (id)
);
-- Twitter configuration
CREATE TABLE datasource_configurations (
  id SERIAL UNIQUE,
  datasource_settings_id INTEGER NOT NULL,
  datasource_application_config JSONB,
  PRIMARY KEY (id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id)
);

CREATE TABLE  applications (
  id SERIAL UNIQUE,
  user_id INTEGER NOT NULL,
  application_name VARCHAR(20),
  training_config_resources JSONB,
  application_dataset INTEGER NOT NULL,
  application_prep_stages_ids INTEGER ARRAY NOT NULL,
  application_models_ids INTEGER ARRAY NOT NULL,
  classification_criteria INTEGER NOT NULL,
  application_status application_status_enum,
  datasource_configuration INTEGER NOT NULL,
  datasource_settings_id INTEGER NOT NULL,
  error_status TEXT,
  PRIMARY KEY (id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (application_dataset) REFERENCES datasets(id),
  FOREIGN KEY (datasource_settings_id) REFERENCES datasource_settings(id),
  FOREIGN KEY (datasource_configuration) REFERENCES datasource_configurations(id)
);


-- INSERT EXAMPLE code_block_templates
INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('initializer', 1, 'input', '{"code": "import nltk ;import random ;from nltk.corpus import movie_reviews ;from nltk.classify.scikitlearn import SklearnClassifier ;from nltk.tokenize import word_tokenize ;import pyspark ;from pyspark.sql import SparkSession ;spark = SparkSession.builder.appName(\"Basic template\").config(\"spark.jars.packages\",\"ml.combust.mleap:mleap-spark-base_2.11:0.7.0,ml.combust.mleap:mleap-spark_2.11:0.7.0\").getOrCreate() ;sc = spark.sparkContext ;input_data = sc.readText(<dataset>) ;input_data_df = spark.createDataFrame(input_data, [\"features\", \"label\"]) ;pipeline_preprocessing_stages = [] ;pipeline_models_stages = [] ;pipeline_stages = []", "params":"[<dataset>]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('pos_tagger', 1, 'preprocessing', '{"code": "import nltk;from pyspark import keyword_only;from pyspark.ml import Transformer;from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param;from pyspark.sql.functions import udf;from pyspark.sql.types import ArrayType, StringType, StructType, StructField;class NLTKPosTagger(Transformer, HasInputCol, HasOutputCol):;  @keyword_only;  def __init__(self, inputCol=None, outputCol=None):;    super(NLTKPosTagger, self).__init__();    kwargs = self._input_kwargs;    self.setParams(**kwargs);  @keyword_only;  def setParams(self, inputCol=None, outputCol=None):;    kwargs = self._input_kwargs;    return self._set(**kwargs);  def _transform(self, dataset):;    def tag_instance(tokenized_instance):;      tagged_tokens = nltk.pos_tag(tokenized_instance);      return tagged_tokens;    types = ArrayType(StructType([StructField(\"char\", dataType=StringType(), nullable=False),StructField(\"type\", dataType=StringType(), nullable=False)]));    out_col = self.getOutputCol();    in_col = dataset[self.getInputCol()];    return dataset.withColumn(out_col, udf(tag_instance, types)(in_col)).drop(\"features\").withColumnRenamed(\"features_output\", \"features\");NLTK_POS_TAGGER = NLTKPosTagger(inputCol=\"features\",outputCol=\"features_output\");pipeline_preprocessing_stages += NLTKPosTagger(inputCol=pipeline_stages[-1].getOutputCol(), \"nltk_pos_tagger_col\")", "params": "[]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('tokenizer', 1, 'preprocessing', '{"code": "from pyspark.ml.feature import Tokenizer;if (bool(pipeline_preprocessing_stages)):;  tokenizer = Tokenizer(inputCol=pipeline_preprocessing_stages[-1].getOutputCol(), outputCol=\"tokenizer_col\");else:;  tokenizer = Tokenizer(inputCol=\"input_features\", outputCol=\"tokenizer_col\");pipeline_preprocessing_stages.append(tokenizer)", "params":"[]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('logistic_regression', 1, 'model', '{"code": "from pyspark.ml.classification import LogisticRegression;lr = LogisticRegression(maxIter=<lr_max_iter>, regParam=<lr_reg_param>);pipeline_models_stages += (lr.uid, lr)", "params":"[<lr_max_iter>,<lr_reg_param>]"}');


INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('pipeline_execution', 1, 'output', '{"code": "from pyspark.ml import Pipeline, PipelineModel;last_column_name = pipeline_preprocessing_stages[-1].getOutputCol();preprocessing_pipeline = Pipeline(stages=pipeline_preprocessing_stages);preprocessing_pipeline_trained = preprocessing_pipeline.fit(input_data_df).transform(input_data_df).withColumnRenamed(last_column_name, \"features\");models_pipelines = [];for model_pipeline in pipeline_models_stages:;  models_pipelines.append(model_pipeline.fit(preprocessing_pipeline_trained))", "params":"[]"}');

INSERT INTO code_block_templates(template_name, model_engine, type, code_content)
VALUES ('output', 1, 'output', '{"code": "import mleap.pyspark; from mleap.pyspark.spark_support import SimpleSparkSerializer;preprocessing_pipeline_trained.serializeToBundle(\"jar:file:s3:/{user_email}/models/{model_id}/preprocessing.zip\".format(user_email, model_id));for model_name, model_pipeline in models_pipelines:;  model_pipeline.serializeToBundle(\"jar:file:s3:/{user_email}/models/{model_name}.zip\".format(user_email, model_name))", "params":"[]"}');
