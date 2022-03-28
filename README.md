# AI ENGINEERING

This is a repository for the AI Engineering team to share code with customers and the community.  This ranges from simple example API snippets to demonstrations and end to end tutorials and associated code.

Additional code examples can be accessed from the following locations:

- [Tutorials for data scientists repo](https://github.com/datarobot-community/tutorials-for-data-scientists/)
- [Examples for data scientists repo](https://github.com/datarobot-community/examples-for-data-scientists/)
- [AI Engineering repo](https://github.com/datarobot-community/ai_engineering)
- [docs.datarobot.com](https://docs.datarobot.com/en/docs/api/code-examples/index.html)
- [R Vignettes included in the R client](https://cran.r-project.org/web/packages/datarobot/index.html)
- [Examples included in the Python client](https://datarobot-public-api-client.readthedocs-hosted.com/en/v2.27.1/examples/index.html)

## Important Links

- To learn to use DataRobot, visit [DataRobot University](https://university.datarobot.com/).
- For articles on using DataRobot, feature deep dives, and example workflows, visit [DataRobot Community](https://community.datarobot.com/).
to:
- To ask questions and get help from DataRobot experts and peers, visit [DataRobot Community](https://community.datarobot.com/)
​
## Usage

Multiple integrations and projects will be hosted within this repo, see individual readmes in subfolders for details relevant to those individual entries.

## Related Community Articles

These are articles created in the DataRobot community by the AI Engineering group, referencing both inline code in the articles, as well as contents in this repository.

### Database Integration Examples

[DataRobot data connections](https://docs.datarobot.com/en/docs/data/connect-data-sources/data-conn.html) - To enable integration with a variety of enterprise databases, DataRobot provides a “self-service” JDBC platform for database connectivity setup. Once configured, you can read data from production databases for model building and predictions.  \
[Create a Feature Discovery project](https://docs.datarobot.com/en/docs/data/transform-data/feature-discovery/fd-overview.html) - Feature Discovery is based on relationships—between datasets and the features within those datasets.  \
[Prediction intake options](https://docs.datarobot.com/en/docs/predictions/batch/batch-prediction-api/intake-options.html) - You can configure a prediction source using the Predictions > Job Definitions tab or the Batch Prediction API. \
[Batch Prediction API : Snowflake scoring](https://docs.datarobot.com/en/docs/predictions/batch/batch-prediction-api/intake-options.html#snowflake-scoring) - Using JDBC to transfer data can be costly in terms of IOPS (input/output operations per second) and expense for data warehouses. This adapter reduces the load on database engines during prediction scoring by using cloud storage and bulk insert to create a hybrid JDBC-cloud storage solution. 

### Data Processing Related
[DataRobot Pipelines v7.3.0+](https://docs.datarobot.com/en/docs/data/pipelines/index.html) - DataRobot Pipelines enable data science and engineering teams to build and run machine learning data flows. Teams start by collecting data from various sources, cleaning them, and combining them.  

### MLOps Custom Model Hosting on DataRobot
[Workshop: Create, test, and deploy a custom model](https://docs.datarobot.com/en/docs/mlops/deployment/custom-models/index.html) - Custom inference models allow you to bring your own pretrained models to DataRobot. By uploading a model artifact, you can create, test, and deploy custom inference models to a centralized deployment hub. DataRobot supports models built with a variety of coding languages, including Python, R, and Java. 

### MLOps Overview, Automatic Retraining, Accuracy Monitoring, MLOps Agent, Agent Use Cases )
[MLOps overview](https://docs.datarobot.com/en/docs/mlops/mlops-overview.html) - DataRobot MLOps provides a central hub to deploy, monitor, manage, and govern all your models in production, regardless of how they were created or when and where they were deployed.  \
[Continuous AI: Set up automatic retraining](https://docs.datarobot.com/en/docs/mlops/manage-mlops/set-up-auto-retraining.html) - To maintain model performance after deployment without extensive manual work, DataRobot provides an automatic retraining capability for deployments. \
[Enable accuracy monitoring](https://docs.datarobot.com/en/docs/mlops/manage-mlops/setup-accuracy.html) - You can monitor a deployment for accuracy using the Accuracy tab, which lets you analyze the performance of the model deployment over time, using standard statistical measures and exportable visualizations. \
[MLOps agent](https://docs.datarobot.com/en/docs/mlops/deployment/mlops-agent/index.html) - DataRobot MLOps provides powerful tools for tracking and managing models for prediction. But what if you already have—or need to have—deployments running in your own environment?  \
[MLOps Agent use cases](https://docs.datarobot.com/en/docs/mlops/deployment/mlops-agent/agent-use.html) - Monitoring use cases below for examples of how to apply the MLOps agent: Reporting metrics, Monitoring a Spark environment, Monitoring using the MLOps CLI

### Portable Prediction Server (PPS) - DataRobot Models in Docker Images Deployed as Containers within Kubernetes
[Portable Prediction Server](https://docs.datarobot.com/en/docs/mlops/deployment/deploy-pred/portable-pps.html) - The Portable Prediction Server (PPS) is a DataRobot execution environment for DataRobot model packages (.mlpkg files) distributed as a self-contained Docker image. \
[Portable batch predictions](https://docs.datarobot.com/en/docs/mlops/deployment/deploy-pred/portable-batch-predictions.html) - Portable batch predictions (PBP) let you score large amounts of data on disconnected environments. \
[Custom model Portable Prediction Server](https://docs.datarobot.com/en/docs/mlops/deployment/deploy-pred/custom-pps.html) - The custom model Portable Prediction Server (PPS) is a solution for deploying a custom model to an external prediction environment. It can be built and run disconnected from main installation environments.  

### Platform Administration
[Administrator's guide](https://docs.datarobot.com/en/docs/admin/for-admins/index.html) - The DataRobot Administrator's Guide is intended to help administrators manage their DataRobot application. Manage users, Reference. 

### DataRobot API 
[API Quickstart (documentation](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html) - The DataRobot API provides a programmatic alternative to the web interface for creating and managing DataRobot projects. The API can be used via REST or with DataRobot's Python or R clients in Windows, UNIX, and OS X environments.  \
[DataRobot University: Python API Starter Quest (Free)](https://university.datarobot.com/path/python-api-starter-quest) - provide the foundation skills for using Python to work with the DataRobot API. The courses are self-paced, so if you prefer instructor-led training, we recommend that you start with API I Python. 

### Batch Scoring
[Scoring at the command line](https://docs.datarobot.com/en/docs/predictions/scoring-code/scoring-cli.html) - Syntax for scoring at the command line. 

### Solutions/Applications
[AI App Builder](https://docs.datarobot.com/en/docs/modeling/biz-ops/app-builder/index.html) - The AI App Builder allows you to build and configure AI-powered applications using a no-code interface to enable core DataRobot services without having to build models and evaluate their performance in DataRobot.  \
[DataRaobot Zepl Notebooks](https://docs.datarobot.com/en/notebooks) - Apply and share notebook-powered analytics across the enterprise. \
[Algorithmia](https://docs.datarobot.com/en/docs/mlops/deployment/algorithmia.html) - DataRobot Algorithmia is an MLOps platform where you can deploy, govern, and monitor your models as microservices. The platform lets you connect models to data sources and deploy them quickly to production.  

### Exported Code Deployment Examples
[DataRobot Prime](https://docs.datarobot.com/en/docs/predictions/ui/prime.html) - DataRobot Prime optimizes prediction models for use outside of the DataRobot application, which can provide multiple benefits. Once created, you can export these models as a Python module or a Java class, and run the exported script.  \
[DataRobot Prime examples](https://docs.datarobot.com/en/docs/predictions/ui/prime-examples.html) - You can generate source code for the model as a Python module or Java class. \
[Scoring Code JAR integrations](https://docs.datarobot.com/en/docs/predictions/scoring-code/sc-jar-integrations/index.html) - Although DataRobot provides its own scalable prediction servers that are fully integrated with other platforms, there are several reasons you may decide to deploy Scoring Code on another platform... 

## Development and Contributing
If you'd like to report an issue or bug, suggest improvements, or contribute code to this project, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

# Code of Conduct
This project has adopted the Contributor Covenant for its Code of Conduct. 
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) to read it in full.

# License
Licensed under the Apache License 2.0. 
See [LICENSE](LICENSE) to read it in full.
