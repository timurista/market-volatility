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

resource "aws_lambda_function" "stock_lambda_udpater" {
  filename      = "bundle.zip"
  function_name = "handler"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "handler"

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