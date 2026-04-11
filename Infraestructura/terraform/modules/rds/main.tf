#####################################
# Database Network Configuration
#####################################

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.db_identifier}-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.db_identifier}-sg"
  description = "Permitir trafico de entrada a Postgres"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = toset(var.allowed_security_group_ids)
    content {
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [ingress.value]
    }
  }

  dynamic "ingress" {
    for_each = toset(var.allowed_cidr_blocks)
    content {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "all"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#####################################
# Database Configuration
#####################################

resource "aws_db_instance" "mi_rds_postgres" {
  identifier              = var.db_identifier
  allocated_storage       = var.db_allocated_storage_gib
  engine                  = "postgres"
  engine_version          = "17.4"
  instance_class          = "db.t3.micro"
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  skip_final_snapshot     = true
  db_subnet_group_name    = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  publicly_accessible     = var.db_publicly_accessible
  backup_retention_period = 1
  storage_type            = "gp3"

  lifecycle {
    precondition {
      condition     = length(var.allowed_security_group_ids) > 0 || length(var.allowed_cidr_blocks) > 0
      error_message = "RDS requiere al menos un security group o CIDR autorizado para PostgreSQL."
    }
  }
}
