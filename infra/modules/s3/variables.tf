variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "source_bucket_name" {
  description = "Name of the source S3 bucket"
  type        = string
}

variable "dest_bucket_name" {
  description = "Name of the destination S3 bucket"
  type        = string
}