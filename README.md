# Data Pipeline

A production-grade AWS data pipeline that ingests JSON events from S3, validates and
transforms them, and writes partitioned Parquet output back to S3.

![CI](https://github.com/Sri-Lekha03/data-pipeline/actions/workflows/ci.yml/badge.svg)

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (`pip install uv`)
- Terraform >= 1.6
- AWS CLI configured with credentials
- An AWS account with permissions to create S3, Lambda, IAM, CloudWatch, and SNS resources

## Local Dev Setup

```bash
git clone https://github.com/Sri-Lekha03/data-pipeline.git
cd data-pipeline
uv sync --all-extras
```

Run linting and type checks:
```bash
uv run ruff check .
uv run mypy pipeline --ignore-missing-imports
```

Run tests:
```bash
uv run pytest -q --cov=pipeline --cov-report=term-missing
```

## Run the Pipeline Locally

```bash
uv run python -m pipeline.cli run \
  --source-bucket my-source-bucket \
  --dest-bucket my-dest-bucket \
  --date 2026/04/11
```

## Deploy

### 1. Bootstrap remote state (first time only)

Create the S3 bucket and DynamoDB table for Terraform state manually or via AWS CLI:

```bash
aws s3api create-bucket --bucket tfstate-data-pipeline-329599634313 --region us-east-1
aws dynamodb create-table \
  --table-name tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Upload Lambda zip to S3

```bash
mkdir -p build
uv export --no-dev --format requirements-txt > build/requirements.txt
pip install -r build/requirements.txt -t build/package/
cp -r pipeline build/package/
cd build/package && zip -r ../../lambda.zip .
aws s3 cp lambda.zip s3://<source-bucket>/lambda/lambda.zip
```

### 3. Deploy infrastructure

```bash
cd infra
terraform init
terraform apply -var-file=envs/dev.tfvars   # for dev
terraform apply -var-file=envs/prod.tfvars  # for prod
```

## Destroy Infrastructure

```bash
cd infra
terraform destroy -var-file=envs/dev.tfvars
```

## CI/CD

- **CI** runs on every push: lint → type-check → test → build Lambda zip
- **Deploy** runs on pull requests (plan) and merges to main (apply)

Add these secrets to your GitHub repository settings:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`