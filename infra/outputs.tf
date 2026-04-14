output "source_bucket_name" {
  value = module.s3.source_bucket_name
}

output "dest_bucket_name" {
  value = module.s3.dest_bucket_name
}

output "lambda_function_name" {
  value = module.lambda.function_name
}

output "lambda_function_arn" {
  value = module.lambda.function_arn
}

output "sns_topic_arn" {
  value = module.monitoring.sns_topic_arn
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}