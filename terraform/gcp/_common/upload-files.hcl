# For local development
terraform {
  source = "../../modules//upload-files/"
}

locals {
  global_vars = yamldecode(file(find_in_parent_folders("global-values.yaml")))
}

dependency "storage" {
    config_path = "../storage"
    mock_outputs = {
      gcp_public_container_name = "dummy-container-public"
    }
}

dependency "service-account" {
  config_path = "../service-account"
  mock_outputs = {
    service_account_email = "dummy-service-account-email"
    service_account_key_local_path = "dummy-service-account-key"
  }
}

inputs = {
  gcp_project                          = local.global_vars.global.cloud_storage_project
  gcp_bucket_name                      = dependency.storage.outputs.gcp_public_container_name
  gcp_service_account_key              = dependency.service-account.outputs.service_account_key_local_path
}