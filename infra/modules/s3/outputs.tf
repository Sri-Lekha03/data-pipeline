output "source_bucket_name" {
  value = aws_s3_bucket.source.bucket
}

output "source_bucket_arn" {
  value = aws_s3_bucket.source.arn
}

output "dest_bucket_name" {
  value = aws_s3_bucket.dest.bucket
}

output "dest_bucket_arn" {
  value = aws_s3_bucket.dest.arn
}