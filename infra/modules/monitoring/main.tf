resource "aws_cloudwatch_log_group" "pipeline" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 7

  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_filter" "errors" {
  name           = "${var.function_name}-errors"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.pipeline.name

  metric_transformation {
    name      = "PipelineErrors"
    namespace = "DataPipeline"
    value     = "1"
  }
}

resource "aws_sns_topic" "alerts" {
  name = "${var.function_name}-alerts"

  tags = {
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "records_failed" {
  alarm_name          = "${var.function_name}-records-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "records_failed"
  namespace           = "DataPipeline"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert when any records fail validation"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Environment = var.environment
  }
}