# S3 bucket
resource "aws_s3_bucket" "progimg" {
  bucket = "progimage-temp01"
  acl    = "private"
  force_destroy = true

  # Deploy Lambda + API Gateway using Chalice
  provisioner "local-exec" {
    working_dir = "../src/"
    command     = "chalice deploy --stage aws"
  }

  # Remove Lambda + API Gateway using Chalice
  provisioner "local-exec" {
    when        = destroy
    working_dir = "../src/"
    command     = "chalice delete --stage aws"
  }
}