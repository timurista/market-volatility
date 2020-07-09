variable "GITHUB_ACCESS_TOKEN" {}

# Configure the AWS Provider
provider "aws" {
  version = "~> 2.0"
  region  = "us-east-1"
  profile = "me"
}


resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
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
EOF
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "layer_bundle_01.zip"
  layer_name = "stocklayer1"

  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "lambda_layer_2" {
  filename   = "layer_bundle_02.zip"
  layer_name = "stocklayer2"

  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "lambda_layer_3" {
  filename   = "layer_bundle_03.zip"
  layer_name = "stocklayer3"

  compatible_runtimes = ["python3.7"]
}


resource "aws_lambda_function" "stock_lambda_udpater" {
  filename      = "bundle.zip"
  function_name = "handler"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "src/handler.handler"
  layers = [
      "${aws_lambda_layer_version.lambda_layer.arn}", 
      "${aws_lambda_layer_version.lambda_layer_2.arn}",
      "${aws_lambda_layer_version.lambda_layer_3.arn}"
    ]

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = "${filebase64sha256("bundle.zip")}"

  runtime = "python3.7"

  environment {
    variables = {
      GITHUB_ACCESS_TOKEN = var.GITHUB_ACCESS_TOKEN
    }
  }
}

resource "aws_cloudwatch_event_rule" "every_twenty_minutes" {
  name                = "every_twenty_minutes"
  description         = "Fires every 20 minutes"
  schedule_expression = "rate(20 minutes)"
}

resource "aws_cloudwatch_event_target" "check_every_twenty_minutes" {
  rule      = aws_cloudwatch_event_rule.every_twenty_minutes.name
  target_id = "lambda"
  arn       = aws_lambda_function.stock_lambda_udpater.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stock_lambda_udpater.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_twenty_minutes.arn
}

