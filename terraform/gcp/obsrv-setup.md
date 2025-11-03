This guide walks you through installing **Obsrv** in FMPS using the `obsrv-automation` repository. The setup includes configuring infrastructure with Terraform/Terragrunt and deploying services with Helm.

---

## Prerequisites

- Google Cloud CLI [`gcloud`](https://cloud.google.com/sdk/docs/install#deb) installed and authenticated
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) and [Terragrunt](https://terragrunt.gruntwork.io/docs/getting-started/install/) must be installed.
- Access to the [obsrv-automation](https://github.com/Sanketika-labs/obsrv-automation) GitHub repository.
- Ensure your Google Cloud account has the following permissions:

    ```
    GCS: Create and manage Cloud Storage buckets for storing Terraform state.
    IAM: Create and assign IAM roles and service accounts for resource access control```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Sanketika-labs/obsrv-automation.git
git checkout 1.9.2-fmps2     # prefer to use the latest tag.
cd obsrv-automation/terraform/gcp
```
## Edit Cluster Configuration

Edit the file `vars/cluster_overrides.tfvars` with your environment-specific settings:

```hcl
project           = "<project-id>"           # GCP project ID where resources will be created (e.g., "sunbird-prod")
building_block    = "<building-block>"       # Logical group or domain of the deployment (e.g., "agri", "education")
env               = "<env>"                  # Deployment environment (e.g., "dev", "test", "stage", "prod")
region            = "<region>"               # GCP region where the GKE cluster will be deployed
gke_cluster_location = "<cluster-location>"  # Specific location (zone or region) for the GKE cluster
zone              = "<cluster-zone>"
timezone          = "<time-zone>"            # Time standard used by the cluster ("UTC", "GMC", "WAT", "CAT")
```
ℹ️ `Note`: Update the env, region, zone with the existing cluster details.

## Configure GCS Bucket

Obsrv uses a Google Cloud Storage (GCS) bucket to store Terraform state files. Edit a file named `obsrv.conf` in the `infra-setup/` of the repo with the following content:

```bash
GOOGLE_PROJECT_ID="< name_of_the_project >" eg: sunbbird
GOOGLE_TERRAFORM_BACKEND_BUCKET="< tfstate_bucket_name >" eg: sunbird-tfstate # Recommended to pass bucket name like this `<building-block>-<env>-tfstate`
GOOGLE_TERRAFORM_BACKEND_BUCKET_REGION="< bucket_region >" eg: asia-south1 # Specify the region of the cluster
```

> ℹ️ **Note**: The bucket will be created automatically during the installation if it doesn't already exist.


## 🔧 Run the Installation Script

Navigate into the `infra-setup` directory and run the installation script:

```bash
time ./obsrv.sh install --provider gcp --config ./obsrv.conf
```
## Update Global Cloud Configurations
Edit the file `helmcharts/global-cloud-values-gcp.yaml` and ensure following values are correctly set.
```yaml
global:
  project_id: <your-gcp-project-id> # Here you have pass the project name eg: sunbird
  cloud_storage_region: <asia-south1> # Region of the cluster
  cloud_storage_config: |   # You will find the values in the terraform/gcp/credentials/*.json
    '{"identity":"<replace_with_client_email>","credential":"<replace_with_private_key>","projectId":"<replace_with_project_id>"}' 
  cloud_storage_bucket: <bucket-name> # Pass private bucket name
  postgresql_backup_cloud_bucket: <bucket-name> # Pass the private bucket name
  checkpoint_bucket: gs://<private-bucket-name> # Pass private bucket name
  velero_backup_cloud_bucket: <private-bucket-name> # Pass private bucket name

# Have to manually pass the service account names that are created.
service_accounts:
  config-api: <sa-name> # Follow this format: <replace_with_building_block>-config-api-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  dataset-api: <sa-name> # Follow this format: <replace_with_building_block>-dataset-api-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  druid-raw: <sa-name> # Follow this format: <replace_with_building_block>-druid-raw-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  flink-sa: <sa-name> # Follow this format: <replace_with_building_block>-flink-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  postgres: <sa-name> # Follow this format: <replace_with_building_block>-psql-backup-sa@<replace_with_project_id>.iam.gserviceaccount.com
  secor: <sa-name> # Follow this format: <replace_with_building_block>-secor-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  spark: <sa-name> # Follow this format: <replace_with_building_block>-spark-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
  velero: <sa-name> # Follow this format: <replace_with_building_block>-velero-sa-iam-role@<replace_with_project_id>.iam.gserviceaccount.com
```

Note: Value for cloud_storage_config you will get in `terraform/gcp/credentials/*.json`

## Install Core Services

Navigate to the Helm charts directory and install the core services:

```
cd /helmcharts/kitchen
export cloud_env=gcp
bash install.sh core-setup
```
This installs critical components such as Postgres, Kafka, Zookeeper and others required by Obsrv.


## Configure Domain Mapping

After core services are installed:

1. Run the following to fetch the external IP of Kong (API Gateway):

   ```bash
   kubectl get svc -n kong # Get the external ip
   ```

2. Update the `global-values.yaml` file with the domain using sslip.io for automatic DNS resolution:

   ```yaml
   domain: "<external_ip>.sslip.io" # example: domain: "23.34.123.432.sslip.io"
   ```

## Install All Services

```
 bash install.sh all
```

This installs all the services present in obsrv.
## Completion

Once installation is complete:

- Open your browser and access the Obsrv UI at:

  ```
  https://<external_ip>.sslip.io/console
  ```

- Use `kubectl get pods --all-namespaces` to verify all pods are running.

- Monitor logs or dashboards as required to confirm proper service operation.


## Testing

Please refer the following documentation. [Obsrv](https://docs.obsrv.ai/how-tos/create-a-dataset)
