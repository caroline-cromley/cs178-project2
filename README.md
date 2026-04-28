# CS178 Project 2 — Event-Driven AWS Data Pipeline
**Author:** Caroline Cromley

---

## Project Summary

This project builds a fully automated, event-driven ETL pipeline on AWS. When a CSV file is uploaded to S3, the entire pipeline triggers automatically — a Lambda function starts an AWS Glue job that cleans and transforms the data, writes the output as Parquet back to S3, and makes it queryable via Athena. No manual steps are required after the initial upload.

---

## How to Review This Project

You do not need to run anything locally. All AWS infrastructure was deployed and tested in my personal AWS account. To evaluate the project, please refer to:

1. **The code** in this repository (data generator, Glue ETL script, Lambda handler, Athena queries)
2. **The screenshots** in `docs/screenshots/` showing each stage of the pipeline running successfully
3. **The essay** in `docs/essay.md` for written reflection
4. **The video** linked below for a live walkthrough demo

---

## Video Walkthrough
Located in docs/screenshots.

The video demonstrates:
- Uploading a CSV to the raw S3 bucket
- The Lambda function firing automatically
- The Glue job running and succeeding
- Partitioned Parquet output appearing in the processed S3 bucket
- Athena querying the processed data with SQL

---

## Architecture

| Step | Service | What it does |
|---|---|---|
| 1 | S3 | Receives raw CSV upload to `raw/` prefix |
| 2 | S3 Event Notification | Fires `ObjectCreated` event on upload |
| 3 | Lambda | Receives event, calls `boto3` to start Glue job |
| 4 | AWS Glue | Runs PySpark ETL script to clean and transform data |
| 5 | S3 | Stores cleaned Parquet output partitioned by region |
| 6 | Glue Data Catalog | Tracks schema and metadata |
| 7 | Athena | Queries processed data directly with SQL |

---

## Project Structure
Located under docs/screenshots/architecture.md

---

## The Data

A synthetic sales dataset of 500 records was generated using Python's `faker` library (`data/generate_data.py`). Intentional data quality issues were introduced to give the Glue job meaningful transformation work:

| Issue | How it was introduced |
|---|---|
| Null quantities | 5% of rows have a missing `quantity` value |
| Blank order totals | 5% of rows have an empty `order_total` |
| Negative unit prices | 3% of rows have a negative `unit_price` |
| Inconsistent status casing | `"completed"`, `"COMPLETED"`, `"Pending"`, and `None` all appear |

---

## Glue ETL Transformations

The PySpark script (`glue/etl_job.py`) applies the following transformations:

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

## Athena Query Results

After the pipeline ran, the Glue Data Catalog registered the processed schema and Athena queried the output directly from S3.

**Total revenue by region:**

| Region | Total Revenue |
|---|---|
| West | $218,477.44 |
| Midwest | $182,010.73 |
| South | $178,601.19 |
| Northeast | $175,779.74 |

See `athena/queries.sql` for all queries used.

---

## Key Concepts Demonstrated

**Event-driven architecture** — each service reacts to an event from the previous one. No polling, no scheduled jobs, no manual triggers. Dropping a file is all it takes to run the full pipeline.

**Medallion architecture** — raw and processed data live in separate S3 prefixes. Raw data is never overwritten, preserving the ability to reprocess from the original source.

**Parquet and partition pruning** — output is stored as Parquet (a columnar format more efficient than CSV for analytics) and partitioned by `region`. Athena only reads the partitions relevant to a given query, reducing cost and improving speed.

**Serverless** — Lambda, Glue, and Athena are all fully serverless. No servers were provisioned or managed. Costs scale to zero when the pipeline is idle.

---

## Essay
The essay with citations is attached in the Blackboard submission.