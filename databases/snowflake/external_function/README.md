# Snowflake External Function

Snowflake has the ability to call an API via a User Defined Function (UDF) - leveraged in this case to score records through a DataRobot model hosted on AWS.  The model can live entirely within AWS; however the examples used below simply use AWS API Gateway and a Lambda to serve the model that acts as a proxy to a remote service (DataRobot prediction engine hosted Prediction API).  Note that as of this writing, Snowflake only allows external API calls to trusted cloud gateways, and cannot query DataRobot directly.

See the related [community article](https://community.datarobot.com/t5/ai-ml-knowledge-base/calling-ml-models-via-snowflake-external-functions-amp-streams/ta-p/5822) for more information.  A scoring pipeline using Snowflake Streams and Tasks is demonstrated as well.

## Contents
lambda_function.py -  This function passes the request received from Snowflake to DataRobot, and processes the return to be in the format Snowflake expects. \
PASSENGERS.csv - Sample input data.
