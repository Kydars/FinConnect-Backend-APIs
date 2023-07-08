###############################################
# An example file deploying a lambda function #
###############################################

# Tells Terraform to run build.sh when any of these file below changed
# - path.module is the location of this .tf file
resource "null_resource" "build_import_s3" {
  triggers = {
    handler      = base64sha256(file("${path.module}/../src/import_s3/handler.py"))       # TODO: change here
    requirements = base64sha256(file("${path.module}/../src/import_s3/requirements.txt")) # TODO: change here
    build        = base64sha256(file("${path.module}/../src/import_s3/build.sh"))         # TODO: change here
  }

  provisioner "local-exec" {
    command = "bash ${path.module}/../src/import_s3/build.sh"
  }
}


# Tells Terraform to compress your source code with dependencies
data "archive_file" "import_s3" {
  type        = "zip"
  output_path = "${path.module}/../src/import_s3.zip" # TODO: change here
  source_dir  = "${path.module}/../src/import_s3"     # TODO: change here

  depends_on = [
    null_resource.build_import_s3 # TODO: change here
  ]
}

# Tells Terraform to create an AWS lambda function
# - Filename here corresponds to the output_path in archive_file.import_s3.
# - Pipeline will inject the content of .GROUP_NAME to be var.group_name, you
#     should use it as a prefix in your function_name to prevent conflictions.
# - Use terraform.workspace to distinguish functions in different stages. It'll
#     be injected by the pipeline when you manually run it.
# - You should set source_code_hash so that after your code changed, Terraform
#     can redeploy your function.
# - You can inject environment variables to your lambda function
resource "aws_lambda_function" "import_s3" {
  filename      = data.archive_file.import_s3.output_path
  function_name = "${var.group_name}_${terraform.workspace}_import_s3" # TODO: change here
  handler       = "handler.handler"
  runtime       = "python3.9" # TODO: change here
  timeout = 30

  role             = aws_iam_role.iam_for_lambda.arn
  source_code_hash = data.archive_file.import_s3.output_base64sha256 # TODO: change here

  environment {
    variables = {
      ENV            = "${terraform.workspace}"
      GLOBAL_S3_NAME = "${var.global_s3_name}"
    }
  }
}

# Work as a template
# - For schedule_expression, see https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html
#     This example creates a scheduled function being invoked every 12 hours
resource "aws_cloudwatch_event_rule" "import_s3" {
  name                = "${var.group_name}_${terraform.workspace}_import_s3" # TODO: change here
  description         = "Daily Import of new OHLC data"                      # TODO: change here
  schedule_expression = "cron(5 0 ? * TUE-SAT *)"                            # TODO: change here
}

resource "aws_cloudwatch_event_target" "import_s3" {
  rule      = aws_cloudwatch_event_rule.import_s3.name
  target_id = "${var.group_name}_${terraform.workspace}_import_s3" # TODO: change here
  arn       = aws_lambda_function.import_s3.arn                    # TODO: change here
}

# Allows your function to be invoked by the Event Bridge.
resource "aws_lambda_permission" "import_s3" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.import_s3.function_name # TODO: change here
  principal     = "events.amazonaws.com"
}

# # Allows your function to be invoked by the gateway.
# # - The last part of the source_arn should be consistent with your route key.
# resource "aws_lambda_permission" "import_s3" {
#   statement_id  = "AllowAPIGatewayInvoke"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.import_s3.function_name # TODO: change here
#   principal     = "apigateway.amazonaws.com"

#   source_arn = "${data.aws_apigatewayv2_api.api_gateway_global.execution_arn}/*/*/import_s3" # TODO: change here
# }

# # This bridges the route on the gateway and your function(or other resources).
# #   Also read: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations.html
# # - The pipeline will inject var.gateway_api_id
# # - integration_method is not the same as the methods in the gateway, it
# #     should be POST for lambda function.
# # - You can optionally rewrite parameters if you want part of your route key to
# #     be passed into the function. E.g. /pets/{param} => /pets/*?param={param}
# resource "aws_apigatewayv2_integration" "import_s3" {
#   api_id           = var.gateway_api_id
#   integration_type = "AWS_PROXY"

#   integration_uri    = aws_lambda_function.import_s3.invoke_arn # TODO: change here
#   integration_method = "POST"

#   # request_parameters = {
#   #   "append:querystring.param" = "$request.path.param"
#   # }
# }

# # This defines the route, linking the integration and the route
# # - You may use wildcard in the route key. e.g. POST /${var.group_name}/*
# # - You should add /${var.group_name}/ as prefix of your route key to prevent 
# #     conflictions in route key
# # - You may add parameter in the path. e.g. GET /${var.group_name}/{param}
# #     If so, you should define it in integrations as well. See the example
# #     above in the integration.
# resource "aws_apigatewayv2_route" "import_s3" {
#   api_id    = var.gateway_api_id
#   route_key = "POST /${var.group_name}/import_s3" # TODO: change here

#   target = "integrations/${aws_apigatewayv2_integration.import_s3.id}" # TODO: change here

#   # If you want your route to be protected. A global authorizer using JWT has
#   #   been integrated to the gateway. Just uncomment the following secion.
  
#   authorization_type = "CUSTOM"
#   authorizer_id      = "${var.gateway_auth_id}"
# }

# Including this resource will keep a log as your function being called
resource "aws_cloudwatch_log_group" "import_s3_log" {
  name              = "/aws/lambda/${aws_lambda_function.import_s3.function_name}" # TODO: change here
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
