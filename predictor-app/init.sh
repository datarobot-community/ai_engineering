# start virtual environment and download requirements
python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
echo "Requirements installed.\n"

read -p "Enter your aws profile: " profile
read -p "Enter your aws region: " region

echo "Creating AWS assets..."
# create dynamodb table 
rand_num=$(openssl rand -hex 3)
dynamodb_table=$(aws dynamodb create-table \
	--table-name async_responses_$rand_num \
	--key-schema AttributeName=id,KeyType=HASH \
	--attribute-definitions AttributeName=id,AttributeType=S \
	--billing-mode PAY_PER_REQUEST \
	--profile "${profile}" \
	--query 'TableDescription.{ARN:TableArn,Name:TableName}' \
	--output text)
export table_arn=$(echo $dynamodb_table | cut -f1 -d ' ')
table=$(echo $dynamodb_table | cut -f2 -d ' ')
echo "DynamoDB Table: $table"

# create s3 bucket
rand_num=$(openssl rand -hex 3)
aws s3api create-bucket \
	--bucket zappa-"${rand_num}" \
	--profile "${profile}"  \
	--create-bucket-configuration LocationConstraint="${region}" >>log 2>&1
export s3_bucket="zappa-${rand_num}"
echo "S3 Bucket: $s3_bucket"

# create iam role
rand_num=$(openssl rand -hex 3)
policy=$(cat ./trusted_relationship.json)
iam_role=$(aws iam create-role \
	--role-name zappa-role-"${rand_num}" \
	--profile "${profile}" \
	--assume-role-policy-document "${policy}" \
	--query 'Role.{ARN:Arn,Name:RoleName}' \
	--output text)
export role_arn=$(echo $iam_role | cut -f1 -d ' ')
export role=$(echo $iam_role | cut -f2 -d ' ')
echo "IAM Role Name: ${role}"
echo "IAM Role ARN: ${role_arn}"

policy=$(envsubst <"policy.json")

# update role to include required policies
policy_arn=$(aws iam create-policy \
	--policy-name zappa-policy-$rand_num \
	--policy-document "${policy}" \
	--query 'Policy.{ARN:Arn}' \
	--output text)
aws iam attach-role-policy \
	--policy-arn $policy_arn \
	--role-name zappa-role-$rand_num >>log 2>&1

# create service bucket and iam user
rand_num=$(openssl rand -hex 3)
aws iam create-user \
	--user-name zappa-service-user-$rand_num \
	--profile $profile
keys=$(aws iam create-access-key \
	--user-name zappa-service-user-$rand_num \
	--query 'AccessKey.{access_key:AccessKeyId,secret_key:SecretAccessKey}' \
	--output text)
export access_key=$(echo $keys | cut -f1 -d ' ')
export secret_key=$(echo $keys | cut -f2 -d ' ')
echo "Access Key ID: ${access_key}"
echo "Secret Access Key: ${secret_key}"
aws s3api create-bucket \
	--bucket zappa-predictions-$rand_num \
	--profile "${profile}"  \
	--create-bucket-configuration LocationConstraint="${region}" >>log 2>&1
export predictions_s3_bucket="zappa-predictions-$rand_num"
bucket_policy=$(envsubst <"bucket-policy.json")

policy_arn=$(aws iam create-policy \
	--policy-name zappa-policy-$rand_num \
	--policy-document "${bucket_policy}" \
	--query 'Policy.{ARN:Arn}' \
	--output text)
aws iam attach-user-policy \
	--policy-arn $policy_arn \
	--user-name zappa-service-user-$rand_num