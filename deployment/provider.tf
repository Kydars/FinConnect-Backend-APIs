terraform {
  required_providers {
    klayers = {
      version = "~> 1.0.0"
      source  = "ldcorentin/klayer"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    # Intentially leave empty, will be filled by the pipeline
  }
}

provider "aws" {
  region = "ap-southeast-2"
}
