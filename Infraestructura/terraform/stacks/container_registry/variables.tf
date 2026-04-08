variable "keep_tags_number" {
  description = "The number of image tags to retain in the registry."
  type        = number
  default     = 5
}

variable "authservice_repository_name" {
  description = "The name of the authservice repository in the Amazon ECR service."
  type        = string
  nullable    = false
}

variable "search_repository_name" {
  description = "The name of the search repository in the Amazon ECR service."
  type        = string
  nullable    = false
}

variable "region" {
  description = "AWS Region where the objects will be deployed."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "The username of the author. For academic purposes."
  type        = string
  nullable    = false
}
