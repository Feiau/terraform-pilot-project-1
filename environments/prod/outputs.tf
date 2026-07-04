output "api_endpoint" {
  description = "The API Gateway endpoint URL for prod environment"
  value       = module.lambda_api.api_endpoint
}

output "function_name" {
  description = "The Lambda function name"
  value       = module.lambda_api.function_name
}
