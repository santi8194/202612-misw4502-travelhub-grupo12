module "ecr_repository_authservice" {
  source           = "../../modules/repository"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.authservice_repository_name
}

module "ecr_repository_search" {
  source           = "../../modules/repository"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.search_repository_name
}
