resource "aws_s3_bucket" "source" {
  bucket = var.source_bucket_name

  tags = {
    Environment = var.environment
    Purpose     = "pipeline-source"
  }
}

resource "aws_s3_bucket" "dest" {
  bucket = var.dest_bucket_name

  tags = {
    Environment = var.environment
    Purpose     = "pipeline-dest"
  }
}

resource "aws_s3_bucket_versioning" "source" {
  bucket = aws_s3_bucket.source.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "dest" {
  bucket = aws_s3_bucket.dest.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "source" {
  bucket = aws_s3_bucket.source.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "dest" {
  bucket = aws_s3_bucket.dest.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "source" {
  bucket = aws_s3_bucket.source.id
  rule {
    id     = "expire-raw-after-90-days"
    status = "Enabled"
    filter {
      prefix = "raw/"
    }
    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "dest" {
  bucket = aws_s3_bucket.dest.id
  rule {
    id     = "expire-processed-after-365-days"
    status = "Enabled"
    filter {
      prefix = "processed/"
    }
    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_public_access_block" "source" {
  bucket                  = aws_s3_bucket.source.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "dest" {
  bucket                  = aws_s3_bucket.dest.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}