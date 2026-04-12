# Notes

## Trade-offs Made

- **No incremental processing** — The bonus DynamoDB state tracker was skipped to focus on core requirements. Would add a DynamoDB table to track processed S3 prefixes and skip already-completed ones.

- **Single Lambda per file** — Currently one Lambda invocation per S3 file. For very large files, would split into chunks or use Step Functions for parallel processing.

- **No VPC** — Lambda runs outside a VPC for simplicity. In a real HIPAA environment, would place it inside a VPC with private subnets and VPC endpoints for S3 and CloudWatch.

- **SSE-S3 over KMS** — Used AES256 (SSE-S3) instead of KMS to avoid key management overhead in a demo. Production would use KMS with a customer-managed key.

- **Email alerts only** — SNS topic only has email subscription. Would add PagerDuty or Slack integration for on-call alerting in production.

- **No Glue Data Catalog** — The optional Glue table was skipped. Would add it to enable direct Athena queries on the Parquet output.

- **mypy not strictly enforced** — Used --ignore-missing-imports due to missing stubs for some packages. Would add full strict typing with more time.

## What I Would Do Differently With More Time

- Add DynamoDB-based incremental processing to skip already-processed partitions
- Add Glue Data Catalog table for Athena queries
- Add OpenTelemetry tracing for end-to-end observability
- Add pre-commit hooks for local linting before push
- Add Terraform plan output as PR comment via GitHub Actions