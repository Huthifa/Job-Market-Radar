resource "aws_db_subnet_group" "main" {
  name       = "jmr-db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = { Name = "jmr-db-subnets" }
}

resource "aws_security_group" "db" {
  name        = "jmr-db-sg"
  description = "Postgres; ingress added on Day 4 from the API only"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "jmr-db-sg" }
}

resource "aws_db_instance" "main" {
  identifier     = "jmr-db"
  engine         = "postgres"
  engine_version = "17"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name                     = "jobradar"
  username                    = "jmr_admin"
  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = 1
  skip_final_snapshot     = true
  deletion_protection     = false
  apply_immediately       = true

  tags = { Name = "jmr-db" }
}

resource "aws_secretsmanager_secret" "gemini_api_key" {
  name                    = "jmr/gemini-api-key"
  description             = "Gemini API key for extraction, embeddings and CV matching"
  recovery_window_in_days = 0
}