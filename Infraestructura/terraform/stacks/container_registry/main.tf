module "ecr_repository" {
  for_each = toset(var.repository_names)

  source           = "../../modules/repository"
  keep_tags_number = var.keep_tags_number
  repository_name  = each.value
}
