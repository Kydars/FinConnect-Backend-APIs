output "api_endpoint" {
  value = data.aws_apigatewayv2_api.api_gateway_global.api_endpoint
}

output "upload_s3" {
  value = aws_apigatewayv2_route.upload_s3.route_key
}

output "export_s3" {
  value = aws_apigatewayv2_route.export_s3.route_key
}

output "fetch" {
  value = aws_apigatewayv2_route.fetch.route_key
}

# output "import_s3" {
#   value = aws_apigatewayv2_route.import_s3.route_key
# }