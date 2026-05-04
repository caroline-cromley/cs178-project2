cs178-project2/
├── README.md
├── .gitignore
│
├── data/
│   ├── generate_data.py       # synthetic CSV generator
│   └── sample_output.csv      # example input file
│
├── lambda/
│   └── handler.py             # Lambda function 
│
├── glue/
│   └── etl_job.py             # PySpark ETL script (read CSV, transform, write Parquet)
│
├── athena/
│   └── queries.sql            # example SELECT queries on processed output
│
└── docs/
    ├── architecture.png       # pipeline diagram screenshot
    └── screenshots/photos.md  # AWS console screenshots for video walkthrough