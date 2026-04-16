import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F

# --- config: update these before running ---
S3_INPUT_PATH  = "s3://your-raw-bucket/raw/"
S3_OUTPUT_PATH = "s3://your-processed-bucket/processed/"

# --- job init ---
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init("etl_job", {})

# --- 1. read raw CSV from S3 ---
print(f"Reading raw CSV from {S3_INPUT_PATH}")
raw_df = spark.read.option("header", "true").option("inferSchema", "true").csv(S3_INPUT_PATH)
print(f"Raw record count: {raw_df.count()}")

# --- 2. drop rows missing critical fields ---
df = raw_df.dropna(subset=["order_id", "order_date", "category", "region"])

# --- 3. fix quantity: fill nulls with 0, cast to int ---
df = df.withColumn(
    "quantity",
    F.when(F.col("quantity").isNull(), 0).otherwise(F.col("quantity").cast("int"))
)

# --- 4. fix unit_price: drop rows with negative prices ---
df = df.filter(F.col("unit_price") > 0)

# --- 5. fix order_total: recalculate where missing or empty ---
df = df.withColumn(
    "order_total",
    F.when(
        (F.col("order_total").isNull()) | (F.col("order_total") == ""),
        F.round(F.col("quantity") * F.col("unit_price"), 2)
    ).otherwise(F.col("order_total").cast("double"))
)

# --- 6. normalize status: lowercase, strip whitespace, fill nulls ---
df = df.withColumn(
    "status",
    F.when(F.col("status").isNull(), "unknown")
     .otherwise(F.lower(F.trim(F.col("status"))))
)

# --- 7. cast order_date to date type ---
df = df.withColumn("order_date", F.to_date(F.col("order_date"), "yyyy-MM-dd"))

# --- 8. drop duplicate rows ---
df = df.dropDuplicates()

# --- 9. add processed_at timestamp ---
df = df.withColumn("processed_at", F.current_timestamp())

print(f"Processed record count: {df.count()}")

# --- 10. write to S3 as Parquet, partitioned by region ---
print(f"Writing to {S3_OUTPUT_PATH}")
df.write.mode("overwrite").partitionBy("region").parquet(S3_OUTPUT_PATH)

print("ETL job complete.")
job.commit()