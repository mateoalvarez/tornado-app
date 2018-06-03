"""Cosa"""
import sys
from pyspark import SparkContext

SPARK_CONTEXT = SparkContext()
DATA = [1, 2, 3, 4, 5]
DIST_DATA = SPARK_CONTEXT.parallelize(DATA)
SPARK_CONTEXT.stop()
