resource "aws_ecr_repository" "pipeline" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
  }
}

output "repository_url" {
  value = aws_ecr_repository.pipeline.repository_url
}
