cs178-project2/
├── README.md
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── generate_data.py       # synthetic CSV generator
│   └── sample_output.csv      # example input file
│
├── lambda/
│   └── handler.py             # Lambda function (~10 lines, calls boto3 start_job_run)
│
├── glue/
│   └── etl_job.py             # PySpark ETL script (read CSV, transform, write Parquet)
│
├── athena/
│   └── queries.sql            # example SELECT queries on processed output
│
└── docs/
    ├── essay.md               # written reflection
    ├── architecture.png       # pipeline diagram screenshot
    └── screenshots/           # AWS console screenshots for video walkthrough