# Architecture

## Data Flow
S3 source bucket (raw/YYYY/MM/DD/*.json)
│
│  S3 ObjectCreated event
▼
AWS Lambda (Python 3.12, 512MB, 5min timeout)
│
├── Validate each record (Pydantic v2)
│       ├── Invalid → dead-letter/ prefix (dest bucket)
│       └── Valid   → transform + partition
│
├── Transform
│       ├── Normalize timestamp → UTC ISO-8601
│       ├── Flatten metadata fields (__ separator)
│       └── Add processed_at column
│
├── Write Parquet (Snappy compressed)
│       └── processed/event_type=X/year=Y/month=M/day=D/
│
└── Emit metrics → CloudWatch (records_processed, records_failed, duration_ms)
│
└── Alarm: records_failed > 0 → SNS → Email

## Key Design Decisions

**Dual entrypoint (Lambda + CLI)**
The pipeline core (`handler.py`) is decoupled from both entrypoints. Lambda calls
`lambda_handler()`, CLI calls `run_pipeline()` directly. Same logic, no duplication.

**Pydantic v2 validation**
All records are validated before transformation. Invalid records are written to
`dead-letter/` with a structured error payload including the raw record, error message,
and timestamp. The pipeline never crashes on bad data.

**Parquet partitioning**
Output is partitioned by `event_type / year / month / day`, making it directly
queryable via Athena without a Glue crawler.

**IAM least-privilege**
Lambda role has scoped permissions: read-only on source bucket, write-only on dest
bucket, specific log group ARN for CloudWatch Logs. `cloudwatch:PutMetricData`
requires `Resource: "*"` per AWS — this is an AWS constraint, not a design gap.

**Remote Terraform state**
State stored in S3 with DynamoDB locking. Separate `dev.tfvars` and `prod.tfvars`
for environment isolation. No hardcoded account IDs or regions anywhere.

**SSE-S3 over KMS**
AES256 used for simplicity in this exercise. Production would use a
customer-managed KMS key for audit trail and key rotation control.

## Infrastructure Overview

| Resource | Purpose |
|---|---|
| S3 source bucket | Receives raw JSON event files |
| S3 dest bucket | Stores Parquet output and dead-letter records |
| Lambda function | Runs the pipeline on S3 trigger |
| CloudWatch Log Group | 7-day retention, error metric filter |
| CloudWatch Alarm | Fires when records_failed > 0 |
| SNS Topic | Delivers email alerts on alarm |