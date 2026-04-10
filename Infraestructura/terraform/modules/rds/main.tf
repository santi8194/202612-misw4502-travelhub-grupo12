#####################################
# Database Network Configuration
#####################################

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.db_identifier}-subnet-group"
  subnet_ids = data.aws_subnets.all.ids
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.db_identifier}-sg"
  description = "Permitir trafico de entrada a Postgres"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.sg_ingress_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "all" # Changed from "-1" to "all" for clarity
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#####################################
# Database Configuration
#####################################

resource "aws_db_instance" "mi_rds_postgres" {
  identifier             = var.db_identifier
  allocated_storage      = var.db_allocated_storage_gib
  engine                 = "postgres"
  engine_version         = "17.4" 
  instance_class         = "db.t3.micro" 
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = var.db_publicly_accessible
  backup_retention_period = 1
  storage_type            = "gp3"
}