resource "local_sensitive_file" "rclone_config" {
content  = templatefile("${path.module}/config.tfpl", {
    gcp_project = var.gcp_project
    gcp_service_account_key = var.gcp_service_account_key
  })
  filename = pathexpand("~/.config/rclone/rclone.conf")
}

resource "null_resource" "copy_from_sunbird_container" {
  triggers = {
    command = "${timestamp()}"
  }
  provisioner "local-exec" {
      command = "rclone copy sunbird:${var.sunbird_public_artifacts_bucket}/${var.sunbird_public_artifacts_path} ownaccount:${var.gcp_bucket_name} --transfers 100 --checkers 100 --exclude .terragrunt-source-manifest --gcs-no-check-bucket"
  }
  depends_on = [local_sensitive_file.rclone_config]
}

locals {
  template_files = fileset("${path.module}/sunbird-rc/schemas", "*.json")
}

resource "local_file" "output_files" {
  for_each = toset(local.template_files)
  content  = templatefile("${path.module}/sunbird-rc/schemas/${each.value}", {
     cloud_storage_schema_url = "https://storage.googleapis.com/${var.gcp_bucket_name}"
  })
  filename = "${path.module}/sunbird-rc/schemas/${each.value}"
}

resource "null_resource" "upload_rc_schemas_to_public_bucket" {
  triggers = {
    command = "${timestamp()}"
  }
  provisioner "local-exec" {
      command = "rclone copy ${path.module}/sunbird-rc/schemas ownaccount:${var.gcp_bucket_name}/schemas --transfers 25 --checkers 25 --exclude .terragrunt-source-manifest --gcs-no-check-bucket"
  }
  depends_on = [local_sensitive_file.rclone_config]
}