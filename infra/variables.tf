variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "source_bucket_name" {
  description = "Name of the source S3 bucket"
  type        = string
}

variable "dest_bucket_name" {
  description = "Name of the destination S3 bucket"
  type        = string
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "data-pipeline"
}

variable "alert_email" {
  description = "Email address for pipeline failure alerts"
  type        = string
}