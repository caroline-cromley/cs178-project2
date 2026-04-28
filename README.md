# CS178 Project 2 — Event-Driven AWS Data Pipeline

An event-driven ETL pipeline built with AWS S3, Lambda, Glue, and Athena. Uploading a CSV file to S3 automatically triggers the entire pipeline — no manual steps required.

---
## Architecture 
1. A CSV file is uploaded to the `raw/` prefix of the S3 input bucket
2. S3 fires an `ObjectCreated` event notification
3. The event invokes a Lambda function
4. Lambda calls `boto3` to start the Glue ETL job
5. Glue reads the raw CSV, applies transformations, and writes clean Parquet output partitioned by region to the processed bucket
6. The Glue Data Catalog tracks the schema throughout
7. Athena queries the processed data directly using SQL

---

## Project Structure
Located under docs/screenshots/architecture.md

---
## AWS Services Used

| Service | Role |
|---|---|
| S3 | Raw input storage and processed Parquet output storage |
| S3 Event Notifications | Triggers Lambda on file upload |
| Lambda | Lightweight compute that starts the Glue job |
| AWS Glue | Serverless PySpark ETL job |
| Glue Data Catalog | Schema and metadata registry |
| Athena | Serverless SQL queries directly against S3 |

---

## Data

A synthetic sales dataset of 500 records was generated using Python's `faker` library. Intentional data quality issues were introduced to give the Glue job meaningful transformation work:

| Issue | Description |
|---|---|
| Null quantities | 5% of rows have a missing `quantity` value |
| Blank order totals | 5% of rows have an empty `order_total` |
| Negative unit prices | 3% of rows have a negative `unit_price` |
| Inconsistent status casing | `"completed"`, `"COMPLETED"`, `"Pending"`, and `None` all appear |

---

## Glue ETL Transformations

The PySpark job applies the following transformations in order:

1. Drop rows missing critical fields (`order_id`, `order_date`, `category`, `region`)
2. Fill null `quantity` values with `0`, cast to integer
3. Filter out rows where `unit_price` is negative
4. Recalculate `order_total` where blank using `quantity * unit_price`
5. Normalize `status` to lowercase, strip whitespace, fill nulls with `"unknown"`
6. Cast `order_date` from string to proper date type
7. Drop fully duplicate rows
8. Add a `processed_at` timestamp column
9. Write output as Parquet partitioned by `region`

---

## Setup & Deployment

### Prerequisites
- AWS account with appropriate IAM permissions
- Python 3.9+ (for local data generation only)
- `pip install faker` (only needed to regenerate the synthetic dataset)

### Step 1 — Generate synthetic data
```bash
python data/generate_data.py
```
Outputs `data/sample_output.csv` with 500 fake sales records.

### Step 2 — Create S3 buckets
Create two S3 buckets in the AWS console:
- `project2rawbucket` — with a `raw/` folder for incoming files
- `project2processedbucket` — for cleaned Parquet output

### Step 3 — Create IAM roles
- **Glue role**: trusted entity `Glue`, attach `AWSGlueServiceRole` + `AmazonS3FullAccess`
- **Lambda role**: trusted entity `Lambda`, attach `AWSGlueServiceRole` + `AmazonS3ReadOnlyAccess`

### Step 4 — Create the Glue ETL job
1. Go to AWS Glue → ETL Jobs → Script editor → Spark
2. Paste `glue/etl_job.py` and update the two S3 path variables at the top
3. Under Job details: select your Glue IAM role, Glue version 4.0, G.1X worker, 2 workers
4. Save the job

### Step 5 — Deploy the Lambda function
1. Go to Lambda → Create function → Python 3.12 runtime
2. Paste `lambda/handler.py`, update `GLUE_JOB_NAME` to match your Glue job name exactly
3. Set timeout to 30 seconds under Configuration → General configuration
4. Attach your Lambda IAM role

### Step 6 — Add the S3 trigger
1. In Lambda → Configuration → Triggers → Add trigger
2. Source: S3, bucket: `project2rawbucket`, event type: PUT, prefix: `raw/`
3. Save

### Step 7 — Test the pipeline
Upload `sample_output.csv` to `s3://project2rawbucket/raw/` and watch the Glue job run automatically. Check Glue → ETL Jobs → Job run history to confirm success, then verify partitioned Parquet folders appear in the processed bucket.

### Step 8 — Query with Athena
1. Go to AWS Glue → Crawlers → Create crawler
2. Point it at `s3://project2processedbucket/processed/`, run it
3. Open Athena, select your database, and run queries from `athena/queries.sql`

---

## Example Athena Query Results

**Total revenue by region:**

| Region | Total Revenue |
|---|---|
| West | $218,477.44 |
| Midwest | $182,010.73 |
| South | $178,601.19 |
| Northeast | $175,779.74 |

---

## Key Concepts

**Event-driven architecture** — each service reacts to an event from the previous one rather than being manually triggered. This makes the pipeline loosely coupled, scalable, and fully automated.

**Medallion architecture** — raw and processed data are stored in separate S3 prefixes. Raw data is never overwritten, so the pipeline can always be rerun against the original source.

**Parquet + partition pruning** — output is stored as Parquet (a columnar format that compresses better than CSV) and partitioned by `region`. When Athena queries a specific region, it only reads the relevant partition rather than scanning the entire dataset.

**Serverless** — every service in this pipeline (Lambda, Glue, Athena) is serverless. There are no servers to provision or manage, and costs scale to zero when the pipeline is not running.

---

## References

- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Faker Library](https://faker.readthedocs.io/en/master/)
- [Apache Parquet Format](https://parquet.apache.org/docs/)