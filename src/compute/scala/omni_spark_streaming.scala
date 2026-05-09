package com.omni.compute

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger

object OmniSparkStreaming {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder
      .appName("Omni Realtime Analytics")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    // Read from Kafka
    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "localhost:9092")
      .option("subscribe", "omni.telemetry")
      .load()

    val parsedDf = df.selectExpr("CAST(value AS STRING)").as[String]

    val query = parsedDf.writeStream
      .outputMode("append")
      .format("console")
      .trigger(Trigger.ProcessingTime("10 seconds"))
      .start()

    query.awaitTermination()
  }
}
