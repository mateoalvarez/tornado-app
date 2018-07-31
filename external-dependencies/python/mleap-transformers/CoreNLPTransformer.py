from pyspark.ml.param.shared import HasInputCol, HasOutputCol, HasNumFeatures
from pyspark import keyword_only
from pyspark.ml.wrapper import JavaTransformer
from pyspark.mllib.common import inherit_doc

@inherit_doc
class PosTaggerCoreNLPSparkTransformer(JavaTransformer, HasInputCol, HasOutputCol):

    _java_class = "org.apache.spark.ml.mleap.feature.PosTaggerCoreNLPSparkTransformer"

    """
    val englishTagKeys: Map[String, Seq[String]] = Map("adjectives" -> Seq("JJ", "JJR", "JJS"),
    "conjunctions" -> Seq("CC"),
    "determiners" -> Seq("DT", "WDT", "PDT"),
    "punctuation" -> Seq(),
    "interjections" -> Seq("UH"),
    "nouns" -> Seq("NN","NNS", "NNP", "NNPS"),
    "pronouns" -> Seq("PRP","PRP$", "WP", "WP$"),
    "adverbs" -> Seq("RB","RBR", "RBS", "WRB"),
    "prepositions" -> Seq("IN", "TO", "RP"),
    "verbs" -> Seq("EX","MD", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"),
    "dates" -> Seq(),
    "numerals" -> Seq("CD"),
    "other" -> Seq("FW", "LS", "POS", "SYM"))

  val spanishTagKeys: Map[String, Seq[String]] = Map("adjectives" -> Seq("ao0000", "aq0000"),
    "conjunctions" -> Seq("cc", "cs"),
    "determiners" -> Seq("da0000","dd0000","de0000","di0000","dn0000","do0000","dp0000","dt0000"),
    "punctuation" -> Seq("f0","faa","fat","fc","fca","fct","fd","fe","fg","fh","fia","fit","fp","fpa","fpt","fra","frc","fs","ft","fx","fz"),
    "interjections" -> Seq("i"),
    "nouns" -> Seq("nc00000","nc0n000","nc0p000","nc0s000","np00000"),
    "pronouns" -> Seq("p0000000","pd000000","pe000000","pi000000","pn000000","pp000000","pr000000","pt000000","px000000"),
    "adverbs" -> Seq("rg","rn"),
    "prepositions" -> Seq("sp000"),
    "verbs" -> Seq("va00000","vag0000","vaic000","vaif000","vaii000","vaip000","vais000","vam0000","van0000","vap0000","vasi000","vasp000","vmg0000","vmic000","vmif000","vmii000","vmip000","vmis000","vmm0000","vmn0000","vmp0000","vmsi000","vmsp000","vsg0000","vsic000","vsif000","vsii000","vsip000","vsis000","vsm0000","vsn0000","vsp0000","vssf000","vssi000","vssp000"),
    "dates" -> Seq("w"),
    "numerals" -> Seq("z0","zm","zu"),
    "other" -> Seq("word"))

    """

    @keyword_only
    def __init__(self, inputCol="input", outputCol="output"):
        super(PosTaggerCoreNLPSparkTransformer, self).__init__()
        self._pos_tagger_java_model =  self._new_java_obj("ml.combust.mleap.core.feature.PosTaggerCoreNLPModel", "en", "nouns,verbs,adjectives")
        self._java_obj = self._new_java_obj("org.apache.spark.ml.mleap.feature.PosTaggerCoreNLPSparkTransformer", self.uid, self._pos_tagger_java_model)
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol="input", outputCol="output"):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

if __name__ == "__main__":

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Basic template").config("spark.jars", "/home/cespinoza/cflores_projects/tornado-app/external-dependencies/mleap-jars/mleap-fatjar/mleap-spark-extension-0.8.1-pyxis-version.jar").getOrCreate()
    sc = spark.sparkContext
    input_data = sc.textFile("/home/cespinoza/Descargas/Telegram\ Desktop/full_pos_neg.txt").map(lambda line: line.split("	"))
    from pyspark import Row

    input_data_splitted = input_data.map(lambda line: Row(features=line[0], label=int(float(line[1]))))
    from pyspark.sql.types import StringType, IntegerType
    from pyspark.sql.types import *

    schema = StructType([StructField("label", IntegerType(), False), StructField("features", StringType(), False)])
    input_data_df = spark.createDataFrame(input_data_splitted, schema=schema)
    pipeline_preprocessing_stages = []
    pipeline_models_stages = []
    pipeline_stages = []

    CORENLP_POS_TAGGER = PosTaggerCoreNLPSparkTransformer(inputCol="features", outputCol="corenlp_pos_tagger_col")
    pipeline_preprocessing_stages.append(CORENLP_POS_TAGGER)

    from pyspark.ml import Pipeline, PipelineModel

    last_column_name = pipeline_preprocessing_stages[-1].getOutputCol()
    preprocessing_pipeline = Pipeline(stages=pipeline_preprocessing_stages)
    input_data_df.show()
    preprocessing_pipeline_trained = preprocessing_pipeline.fit(input_data_df).transform(input_data_df)
    mid_point = preprocessing_pipeline_trained
    mid_point.show()
    for stage in pipeline_preprocessing_stages[:-1]:
        preprocessing_pipeline_trained = preprocessing_pipeline_trained.drop(stage.getOutputCol())
    preprocessing_pipeline_trained = preprocessing_pipeline_trained.drop("features").withColumnRenamed(last_column_name,
                                                                                                       "features")
    preprocessing_pipeline_serializable = preprocessing_pipeline.fit(input_data_df)

    from mleap import pyspark
    from mleap.pyspark.spark_support import SimpleSparkSerializer
    preprocessing_pipeline_serializable.serializeToBundle("jar:file:/tmp/preprocessing_2.zip", dataset=mid_point)
