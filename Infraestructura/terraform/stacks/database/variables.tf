variable "aws_region" {
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
}

variable "db_publicly_accessible" {
  description = "Indica si la BD debe ser accesible públicamente."
  type        = bool
}

variable "sg_ingress_cidr_blocks" {
  description = "Lista de bloques CIDR permitidos para acceder a la instancia RDS PostgreSQL."
  type        = list(string)
}

variable "secret_name" {
  description = "Nombre del secreto en AWS Secrets Manager."
  type        = string
}

variable "db_allocated_storage_gib" {
  description = "Almacenamiento inicial en GB para la BD en gibibytes."
  type        = number
}

variable "db_name" {
  description = "Nombre de la base de datos en RDS."
  type        = string
}

variable "db_host" {
  description = "Endpoint host de la instancia RDS para operaciones SQL administrativas."
  type        = string
}

variable "db_port" {
  description = "Puerto de conexión PostgreSQL para operaciones SQL administrativas."
  type        = number
  default     = 5432
}

variable "db_admin_database" {
  description = "Base administrativa usada para conectarse y crear bases lógicas adicionales."
  type        = string
  default     = "postgres"
}

variable "additional_db_names" {
  description = "Lista de bases de datos adicionales a crear en la misma instancia RDS."
  type        = list(string)
  default     = []
}

variable "db_username" {
  description = "Usuario administrador para la base de datos RDS."
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Contraseña para el usuario administrador de la base de datos RDS."
  type        = string
  sensitive   = true
}

variable "owner" {
  description = "Propietario de los recursos, generalmente el nombre del usuario o equipo."
  type        = string
}

variable "db_identifier" {
  description = "Identificador único de la instancia RDS. Se usa como prefijo en nombres de recursos relacionados."
  type        = string
}