# AI ENGINEERING

This is a repository for the AI Engineering team to share code with customers and the community.  This ranges from simple example API snippets to demonstrations and end to end tutorials and associated code.


## Usage

Multiple integrations and projects will be hosted within this repo, see individual readmes in subfolders for details relevant to those individual entries.

## Related Community Articles

These are articles created in the DataRobot community by the AI Engineering group, referencing both inline code in the articles, as well as contents in this repository.

### Database Integration Examples
[DataRobot & Snowflake: Project Creation](https://community.datarobot.com/t5/resources/datarobot-amp-snowflake-project-creation/ta-p/917) - JDBC via GUI, Snowflake python connector, DataRobot python SDK \
[DataRobot & Snowflake: Server-Side Model Scoring](https://community.datarobot.com/t5/resources/datarobot-amp-snowflake-server-side-model-scoring/ta-p/929) - Scoring via DataRobot Batch Prediction API through the GUI, Snowflake query, and S3 with pre/post SQL \
[Calling ML Models via Snowflake External Functions & Streams](https://community.datarobot.com/t5/resources/calling-ml-models-via-snowflake-external-functions-amp-streams/ta-p/5822) - Snowflake Snowpipe, Streams, Tasks, and External Functions for DR model deployment \
[Scoring Snowflake Data via DataRobot Models on AWS EMR Spark](https://community.datarobot.com/t5/resources/scoring-snowflake-data-via-datarobot-models-on-aws-emr-spark/ta-p/5253) - AWS S3, Secrets Manager, EMR pipeline to score Snowflake data through a DataRobot java scoring code binary model 

### Data Processing Related
[DataRobot Machine Learning with AWS Athena and Parquet Data](https://community.datarobot.com/t5/resources/datarobot-machine-learning-with-aws-athena-and-parquet-data/ta-p/1063) - Ingesting parquet data for project creation via AWS Athena (presto) from S3 

### MLOps Custom Model Hosting on DataRobot
[How to run an ML.NET model with DataRobot MLOps](https://community.datarobot.com/t5/resources/how-to-run-an-ml-net-model-with-datarobot-mlops/ta-p/6026) - Deploying a custom ML.NET model in DataRobot for hosting and monitoring 

### MLOps Reporting (Channel Infrastructure, Drift Tracking, Accurracy/Results Reporting)
[Model Monitoring with Serverless MLOps Agents](https://community.datarobot.com/t5/resources/model-monitoring-with-serverless-mlops-agents/ta-p/7147) - Monitoring externally deployed models with Lambda serverless agents reporting MLOps results \
[MLOps Agent with GKE and Pub/Sub](https://community.datarobot.com/t5/resources/mlops-agent-with-gke-and-pub-sub/ta-p/9649) - Creating a MLOps reporting channel and monitoring agent to report data to DR in GCP \
[AWS Lambda Serverless Reporting Actuals to DataRobot MLOps](https://community.datarobot.com/t5/resources/aws-lambda-serverless-reporting-actuals-to-datarobot-mlops/ta-p/9999) - Actuals reporting back to DataRobot based on serverless trigger architecture \
[Deploy in SageMaker and Monitor with MLOps Agents](https://community.datarobot.com/t5/resources/deploy-in-sagemaker-and-monitor-with-mlops-agents/ta-p/5771) - Monitoring a DataRobot java scoring code model from within a SageMaker container \
[Monitoring a SageMaker Deployed Model in DataRobot MLOps](https://community.datarobot.com/t5/resources/monitoring-a-sagemaker-deployed-model-in-datarobot-mlops/ta-p/9591) - Monitoring a SageMaker developed model hosted on a SageMaker real time endpoint \
[Measuring Prediction Accuracy: Uploading Actual Results](https://community.datarobot.com/t5/resources/measuring-prediction-accuracy-uploading-actual-results/ta-p/7907) - Uploading actual results to DataRobot related to predictions 

### Portable Prediction Server (PPS) - DataRobot Models in Docker Images Deployed as Containers within Kubernetes
[Deploy and Monitor DataRobot Models in AKS](https://community.datarobot.com/t5/resources/deploy-and-monitor-datarobot-models-in-aks/ta-p/7317) - Deploy DataRobot model (PPS) as docker container on Azure AKS \
[Deploy and Monitor DataRobot Models on Google Cloud Platform](https://community.datarobot.com/t5/resources/deploy-and-monitor-datarobot-models-on-google-cloud-platform/ta-p/7675) - Deploy DataRobot model (PPS) as docker container on GCP GKE \
[Deploy and Monitor DataRobot Models on AWS](https://community.datarobot.com/t5/resources/deploy-and-monitor-datarobot-models-on-aws/ta-p/8762) - Deploy DataRobot model (PPS) as docker container on AWS EKS \
[Path-based routing to Portable Prediction Servers on AWS](https://community.datarobot.com/t5/resources/path-based-routing-to-portable-prediction-servers-on-aws/ta-p/9093) - Routing PPS docker container model requests through a single host/IP entry point 

### Platform Administration
[Best Practices for DataRobot Enterprise User Administration](https://community.datarobot.com/t5/resources/best-practices-for-datarobot-enterprise-user-administration/ta-p/9897) - Administration of users/groups/roles 

### Prediction API - Real-Time Requests
[DataRobot Prediction API Usage & HTTP Status Interpretation](https://community.datarobot.com/t5/resources/datarobot-prediction-api-usage-amp-http-status-interpretation/ta-p/966) - Prediction API usage examples scoring through a DataRobot deployment \
[Optimizing Real-Time Model Scoring Request Speed](https://community.datarobot.com/t5/resources/optimizing-real-time-model-scoring-request-speed/ta-p/941) - Considerations for real time scoring request performance 

### Batch Scoring
[Using the Parameterized Batch Scoring Command Line Scripts](https://community.datarobot.com/t5/resources/using-the-parameterized-batch-scoring-command-line-scripts/ta-p/7880) - Using the command line csv scorer for DataRobot deployments 

### Solutions/Applications
[Building a Serverless Predictor App](https://community.datarobot.com/t5/resources/building-a-serverless-predictor-app/ta-p/7870) - Zappa, AWS Lambda and API Gateway prediction application example \
[Turning Raw Predictions into Decisions with an API Wrapper](https://community.datarobot.com/t5/resources/turning-raw-predictions-into-decisions-with-an-api-wrapper/ta-p/9195) - Docker, python, django prediction wrapping decision engine 

### Exported Code Deployment Examples
[Using DataRobot Prime Models with AWS Lambda](https://community.datarobot.com/t5/resources/using-datarobot-prime-models-with-aws-lambda/ta-p/5567) - Prime (java version) deployment via Lambda \
[Using Scoring Code Models with AWS Lambda](https://community.datarobot.com/t5/resources/using-scoring-code-models-with-aws-lambda/ta-p/5559) - Java binary scoring code deployment via Lambda \
[Using Scoring Code Models with AWS Sagemaker](https://community.datarobot.com/t5/resources/using-scoring-code-models-with-aws-sagemaker/ta-p/5558) - AWS SageMaker hosting of a DataRobot java binary scoring code model 


## Development and Contributing

If you'd like to report an issue or bug, suggest improvements, or contribute code to this project, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).


# Code of Conduct

This project has adopted the Contributor Covenant for its Code of Conduct. 
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) to read it in full.

# License

Licensed under the Apache License 2.0. 
See [LICENSE](LICENSE) to read it in full.


