import boto3

GLUE_JOB_NAME = "Project2ETLJob"  

glue = boto3.client("glue")

def lambda_handler(event, context):
    # get the filename that triggered the event
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    print(f"Triggered by: s3://{bucket}/{key}")

    # start the Glue job
    response = glue.start_job_run(JobName=GLUE_JOB_NAME)
    job_run_id = response["JobRunId"]
    print(f"Started Glue job: {GLUE_JOB_NAME}, run ID: {job_run_id}")

    return {
        "statusCode": 200,
        "body": f"Glue job {GLUE_JOB_NAME} started. Run ID: {job_run_id}"
    }