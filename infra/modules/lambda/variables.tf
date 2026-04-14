variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "source_bucket_arn" {
  description = "ARN of the source S3 bucket"
  type        = string
}

variable "source_bucket_name" {
  description = "Name of the source S3 bucket"
  type        = string
}

variable "dest_bucket_arn" {
  description = "ARN of the destination S3 bucket"
  type        = string
}

variable "dest_bucket_name" {
  description = "Name of the destination S3 bucket"
  type        = string
}

variable "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  type        = string
}

variable "image_uri" {
  description = "ECR image URI for the Lambda function"
  type        = string
}