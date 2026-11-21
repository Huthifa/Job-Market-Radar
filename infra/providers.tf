provider "aws" {
  region = "eu-north-1"

  default_tags {
    tags = {
      project = "job-market-radar"
      owner   = "huthifa"
    }
  }
}