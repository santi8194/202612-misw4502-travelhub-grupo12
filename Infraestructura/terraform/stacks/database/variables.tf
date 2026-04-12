variable "aws_region" {
  description = "La region de AWS donde se desplegaran los recursos."
  type        = string
}

variable "db_publicly_accessible" {
  description = "Indica si la BD debe ser accesible publicamente."
  type        = bool
}

variable "vpc_id" {
  description = "VPC donde se desplegara la base de datos."
  type        = string
}

variable "subnet_ids" {
  description = "Subnets donde se desplegara la base de datos."
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks autorizados para exponer PostgreSQL."
  type        = list(string)
  default     = []
}

variable "admin_secret_name" {
  description = "Nombre del secreto admin en AWS Secrets Manager para bootstrap de la instancia."
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

variable "db_username" {
  description = "Usuario administrador para la base de datos RDS."
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Contrasena para el usuario administrador de la base de datos RDS."
  type        = string
  sensitive   = true
}

variable "owner" {
  description = "Propietario de los recursos, generalmente el nombre del usuario o equipo."
  type        = string
}

variable "db_identifier" {
  description = "Identificador unico de la instancia RDS. Se usa como prefijo en nombres de recursos relacionados."
  type        = string
}

variable "service_databases" {
  description = "Configuracion no sensible de bases y secretos por servicio."
  type = map(object({
    secret_name = string
    db_name     = string
    db_username = string
  }))
}

variable "service_db_passwords" {
  description = "Contrasenas sensibles para las credenciales de aplicacion por servicio."
  type        = map(string)
  sensitive   = true
}
