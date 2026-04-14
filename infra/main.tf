module "s3" {
  source             = "./modules/s3"
  environment        = var.environment
  source_bucket_name = var.source_bucket_name
  dest_bucket_name   = var.dest_bucket_name
}

module "ecr" {
  source          = "./modules/ecr"
  repository_name = "${var.function_name}-${var.environment}"
  environment     = var.environment
}

module "monitoring" {
  source        = "./modules/monitoring"
  environment   = var.environment
  function_name = var.function_name
  alert_email   = var.alert_email
}

module "lambda" {
  source             = "./modules/lambda"
  environment        = var.environment
  function_name      = var.function_name
  image_uri          = "${module.ecr.repository_url}:latest"
  source_bucket_arn  = module.s3.source_bucket_arn
  source_bucket_name = module.s3.source_bucket_name
  dest_bucket_arn    = module.s3.dest_bucket_arn
  dest_bucket_name   = module.s3.dest_bucket_name
  log_group_arn      = module.monitoring.log_group_arn
}
