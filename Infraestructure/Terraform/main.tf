terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.73.0"
    }
  }
}

provider "aws" {
  # Configuration options
}

// Buckets

resource "aws_s3_bucket" "input-bucket" {
  bucket = "input-bucket"

  tags = {
    Name        = "Input Bucket"
  }
}

resource "aws_s3_bucket" "output-bucket" {
  bucket = "output-bucket"

  tags = {
    Name        = "Output Bucket"
  }
}

// File inside input-bucket
resource "aws_s3_object" "s3_csv" {
  bucket = aws_s3_bucket.input-bucket.id
  key    = "test_input.csv"
  source = "../../test_input.csv"
}

// Create archives for AWS Lambda functions which will be used for Step Function

data "archive_file" "process_csv" {
  type        = "zip"
  output_path = "../lambda/lambda1.zip"
  source_file = "../lambda/lambda1.py"
}

data "archive_file" "add_column" {
  type        = "zip"
  output_path = "../lambda/lambda2.zip"
  source_file = "../lambda/lambda2.py"
}

// Create IAM role for AWS Lambda

resource "aws_iam_role" "iam_for_lambda" {
  name = "stepFunctionSampleLambdaIAM"

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

// Create AWS Lambda functions

resource "aws_lambda_function" "process_csv" {
  filename         = "../lambda/lambda1.zip"
  function_name    = "process_csv"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "lambda1.lambda_handler"
  runtime          = "python3.8"
}

resource "aws_lambda_function" "add_column" {
  filename         = "../lambda/lambda2.zip"
  function_name    = "add_column"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "lambda2.lambda_handler"
  runtime          = "python3.8"
}



# AWS Step Function
resource "aws_iam_role" "iam_for_sfn" {
  name = "stepFunctionSampleStepFunctionExecutionIAM"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_sfn_state_machine" "csv_processing_workflow" {
  name     = "CSVProcessingWorkflow"
  role_arn = aws_iam_role.iam_for_sfn.arn
  definition = <<JSON
{
  "StartAt": "ProcessCSVFunction",
  "States": {
    "ProcessCSVFunction": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.process_csv.arn}",
      "Next": "AddColumnFunction"
    },
    "AddColumnFunction": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.add_column.arn}",
      "End": true
    }
  }
}
JSON
}