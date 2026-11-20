output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

output "private_subnet_ids" {
  value = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

output "ecr_repository_urls" {
  value = { for name, repo in aws_ecr_repository.repo : name => repo.repository_url }
}

output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}