// Databricks notebook source
"""
Scala  Spark Scoring with DataRobot Scoring Code
"""

// 1) Use local DataRobot Model for Scoring
import com.datarobot.prediction.spark.Predictors
// referencing model_id, which is the same as the generated filename of the JAR file
val DataRobotModel = com.datarobot.prediction.spark.Predictors.getPredictor("5ed708a8fca6a1433abddbcb") 

// 2) read the scoring data
val scoringDF = sql("select * from 10k_lending_club_loans_with_id_csv")

// 3) Score the data and save results to spark dataframe
val output = DataRobotModel.transform(scoringDF)

// 4) Review/consume scoring results 
output.show(1,false)

// COMMAND ----------

"""
Track actual scoring time by wrapping actual scoring method as shown below
"""
def time[A](f: => A): Double = {
  val s = System.nanoTime
  val ret = f
  val scoreTime = (System.nanoTime-s)/1e6 * 0.001
  println("time: "+ scoreTime+"s")
  return scoreTime
}

// 1) Use local DataRobot Model for Scoring
import com.datarobot.prediction.spark.Predictors
// referencing model_id, which is the same as the generated filename of the JAR file
val DataRobotModel = com.datarobot.prediction.spark.Predictors.getPredictor("5ed708a8fca6a1433abddbcb") 

// 2) read the scoring data
val scoringDF = sql("select * from 10k_lending_club_loans_with_id_csv")

val scoreTime = time {
  // Score the data and save results to spark dataframe
  val scoring_output = DataRobotModel.transform(scoringDF)
  scoring_output.show(1,false)
  scoring_output.createOrReplaceTempView("scoring_output")
}

// COMMAND ----------

"""
Report prediction metrics with MLOps
"""
import com.datarobot.mlops.spark.MLOpsSparkUtils

val channelConfig = dbutils.secrets.get(scope="AzureDRdemo", key="mlopschannelconfig")
val scoringDF = sql("SELECT * FROM scoring_output")
MLOpsSparkUtils.reportPredictions(
                scoringDF, // scoring data with predicions
                "5ec3313de71c4404eef2d642", // external DeploymentId 
                "5ec33139f688223b1a84ed78", // external ModelId
                channelConfig, // MLOps channel configuration
                scoreTime, // actual scoring time
                Array("PREDICTION"), //target columns
                "id" // AssociationId
                )

// COMMAND ----------

"""
Report actuals with MLOps
"""
import com.datarobot.mlops.spark.MLOpsSparkUtils
val channelConfig = dbutils.secrets.get(scope="AzureDRdemo", key="mlopschannelconfig")

val actualsDF = spark.sql("select id as associationId, loan_amnt as actualValue, null as timestamp  from 10k_lending_club_loans_with_id_csv as actuals")
MLOpsSparkUtils.reportActuals(
                actualsDF, // scoring data with predicions
                "5ec3313de71c4404eef2d642", // external DeploymentId 
                "5ec33139f688223b1a84ed78", // external ModelId
                channelConfig // MLOps channel configuration
                )
