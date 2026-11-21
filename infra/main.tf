module "network" {
  source = "./modules/network"
}

module "data" {
  source             = "./modules/data"
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
}

module "registry" {
  source = "./modules/registry"
}