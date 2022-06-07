resource aws_lambda_function lambda {
    description   = "craigslist ${var.name}"

    tags = var.tags

    environment {
        PASSWORD = var.password
    }

    filename         = var.filename
    function_name    = "var.name
    role             = aws_iam_role.lambda.arn
    runtime          = "python3.7"
    handler          = "craigslist_rss.run"
    memory_size      = 512
    timeout          = 3 * 60 # 3 minutes
}

resource aws_iam_role lambda {
    name = "iam_for_lambda-${var.name}"

    tags = var.tags

    assume_role_policy = jsonencode(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }
            ]
        }
    )
}

## Logging
resource aws_cloudwatch_log_group lambda_log_group {
    name              = "/aws/lambda/${var.name}"
    retention_in_days = 3
    tags              = var.tags
}

resource aws_iam_policy perms {
    name = "lambda_${var.name}"
    path = "/"
    description = "IAM policy for lambda-${var.name}"

    policy = jsonencode(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": [
                        aws_cloudwatch_log_group.lambda_log_group.arn,
                        "${aws_cloudwatch_log_group.lambda_log_group.arn}:log-stream:*"
                    ],
                    "Effect": "Allow"
                },
                {
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject"
                    ],
                    "Resource": var.s3_resources,
                    "Effect": "Allow"
                }
            ]
        }
    )
}

resource aws_iam_role_policy_attachment perms {
    role = aws_iam_role.lambda.name
    policy_arn = aws_iam_policy.perms.arn
}

resource aws_cloudwatch_event_rule trigger {
  name        = var.name
  description = "trigger lambda ${var.name}"
  schedule_expression = var.cron_schedule
}


resource aws_cloudwatch_event_target trigger {
  rule      = aws_cloudwatch_event_rule.trigger.name
  target_id = "lambda"
  arn       = aws_lambda_function.lambda.arn
  input     = var.lambda_input
}

resource aws_lambda_permission allow_cloudwatch_to_call_lambda {
  statement_id  = "AllowExecutionFromCloudWatch-${aws_cloudwatch_event_rule.trigger.name}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trigger.arn
}