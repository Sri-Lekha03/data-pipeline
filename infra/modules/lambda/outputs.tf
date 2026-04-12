output "function_name" {
  value = aws_lambda_function.pipeline.function_name
}

output "function_arn" {
  value = aws_lambda_function.pipeline.arn
}

output "role_arn" {
  value = aws_iam_role.lambda.arn
}