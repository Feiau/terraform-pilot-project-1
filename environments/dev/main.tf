terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "terraform-state-feitenga01-pilot"
    key          = "dev/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = "dev"
      Owner       = "feitenga01"
      ManagedBy   = "terraform"
    }
  }
}

module "lambda_api" {
  source = "../../modules/lambda-api"

  project_name    = var.project_name
  environment     = "dev"
  lambda_zip_path = var.lambda_zip_path

  tags = {
    Project     = var.project_name
    Environment = "dev"
    Owner       = "feitenga01"
  }
}
