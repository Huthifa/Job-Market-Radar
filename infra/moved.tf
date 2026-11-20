# network
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
moved {
  from = aws_subnet.public_a
  to   = module.network.aws_subnet.public_a
}
moved {
  from = aws_subnet.public_b
  to   = module.network.aws_subnet.public_b
}
moved {
  from = aws_subnet.private_a
  to   = module.network.aws_subnet.private_a
}
moved {
  from = aws_subnet.private_b
  to   = module.network.aws_subnet.private_b
}
moved {
  from = aws_internet_gateway.main
  to   = module.network.aws_internet_gateway.main
}
moved {
  from = aws_route_table.public
  to   = module.network.aws_route_table.public
}
moved {
  from = aws_route.public_internet
  to   = module.network.aws_route.public_internet
}
moved {
  from = aws_route_table_association.public_a
  to   = module.network.aws_route_table_association.public_a
}
moved {
  from = aws_route_table_association.public_b
  to   = module.network.aws_route_table_association.public_b
}
moved {
  from = aws_route_table.private
  to   = module.network.aws_route_table.private
}
moved {
  from = aws_route_table_association.private_a
  to   = module.network.aws_route_table_association.private_a
}
moved {
  from = aws_route_table_association.private_b
  to   = module.network.aws_route_table_association.private_b
}

# data
moved {
  from = aws_s3_bucket.raw
  to   = module.data.aws_s3_bucket.raw
}
moved {
  from = aws_s3_bucket_server_side_encryption_configuration.raw
  to   = module.data.aws_s3_bucket_server_side_encryption_configuration.raw
}
moved {
  from = aws_s3_bucket_public_access_block.raw
  to   = module.data.aws_s3_bucket_public_access_block.raw
}
moved {
  from = aws_db_subnet_group.main
  to   = module.data.aws_db_subnet_group.main
}
moved {
  from = aws_security_group.db
  to   = module.data.aws_security_group.db
}
moved {
  from = aws_db_instance.main
  to   = module.data.aws_db_instance.main
}
moved {
  from = aws_secretsmanager_secret.gemini_api_key
  to   = module.data.aws_secretsmanager_secret.gemini_api_key
}

# registry
moved {
  from = aws_ecr_repository.repo
  to   = module.registry.aws_ecr_repository.repo
}
moved {
  from = aws_ecr_lifecycle_policy.repo
  to   = module.registry.aws_ecr_lifecycle_policy.repo
}