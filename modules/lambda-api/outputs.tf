output "api_endpoint" {
  description = "The HTTP API Gateway endpoint URL"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "function_name" {
  description = "The Lambda function name"
  value       = aws_lambda_function.app.function_name
}

output "function_arn" {
  description = "The Lambda function ARN"
  value       = aws_lambda_function.app.arn
}
