variable "gcp_project" {
    type        = string
    description = "GCP project ID where the bucket is located."
}

variable "gcp_bucket_name" {
    type        = string
    description = "GCP bucket name for storing artifacts."
}

variable "gcp_service_account_key" {
    type        = string
    description = "GCP service account key file path for authentication."
    sensitive   = true
}

variable "sunbird_public_artifacts_bucket" {
    type        = string
    description = "The public GCP bucket name where storage artifacts are published for this release."
    default     = "sunbird-downloadableartifacts"
}

variable "sunbird_public_artifacts_path" {
    type        = string
    description = "The path within the bucket dedicated for this release which holds the storage artifacts."
    default     = "release700"
}
