variable "keep_tags_number" {
  description = "The number of image tags to retain in the registry."
  type        = number
  default     = 5
}

variable "repository_names" {
  description = "The names of the repositories in the Amazon ECR service."
  type        = list(string)
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
