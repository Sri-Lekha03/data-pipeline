variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "alert_email" {
  description = "Email address for pipeline failure alerts"
  type        = string
}