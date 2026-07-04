variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "feitenga01-pilot-hello-world"
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "ap-southeast-2"
}

variable "lambda_zip_path" {
  description = "Path to the Lambda deployment package"
  type        = string
  default     = "../../app/lambda.zip"
}
