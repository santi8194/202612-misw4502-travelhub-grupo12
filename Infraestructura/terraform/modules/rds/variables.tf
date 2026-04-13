# modules/rds/variables.tf
variable "db_identifier" {
  description = "Identificador unico de la instancia RDS. Se usa como prefijo en nombres de recursos relacionados."
  type        = string
}

variable "db_subnet_group_name_override" {
  description = "Nombre explicito para conservar el DB subnet group existente."
  type        = string
  default     = null
}

variable "db_security_group_name_override" {
  description = "Nombre explicito para conservar el security group existente."
  type        = string
  default     = null
}

variable "vpc_id" {
  description = "VPC donde se desplegara la instancia RDS."
  type        = string
}

variable "subnet_ids" {
  description = "Subnets donde se desplegara la instancia RDS."
  type        = list(string)
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

variable "db_publicly_accessible" {
  description = "Indica si la BD debe ser accesible publicamente."
  type        = bool
  default     = false
}

variable "db_apply_immediately" {
  description = "Aplica cambios pendientes inmediatamente en RDS en lugar de esperar a la ventana de mantenimiento."
  type        = bool
  default     = false
}

variable "allowed_security_group_ids" {
  description = "Lista de security groups autorizados a conectarse a PostgreSQL."
  type        = list(string)
  default     = []
}

variable "allowed_cidr_blocks" {
  description = "Lista de CIDR blocks autorizados a conectarse a PostgreSQL."
  type        = list(string)
  default     = []
}
