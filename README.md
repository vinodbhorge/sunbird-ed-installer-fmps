# Sunbird-ED Installer

## Installing Sunbird on Any Cloud Provider

### Pre-requisites

1. **Domain Name**
2. **SSL Certificate**: The FullChain, consisting of the private key and Certificate+CA_Bundle, is mandatory for installation.
3. **Google OAuth Credentials**: [Create credentials](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
4. **Google V3 ReCaptcha Credentials**: [Create credentials](https://www.google.com/recaptcha/admin)
5. **Email Service Provider**
6. **MSG91 SMS Service Provider API Token** (Optional): Required for sending OTPs to registered email addresses during user registration or password reset.
7. **YouTube API Token** (Optional): Necessary for uploading video content directly via YouTube URL.

### Required CLI Tools
1. [jq](https://jqlang.github.io/jq/download/)
2. [yq](https://github.com/mikefarah/yq#install) (for YAML processing)
3. [rclone](https://rclone.org/)
4. [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
5. [Terragrunt](https://terragrunt.gruntwork.io/docs/getting-started/install/)
6. Linux / MacOS / GitBash (Windows)
7. Python 3 
8. PyJWT Python Package (install via pip)
9. [kubectl](https://kubernetes.io/docs/tasks/tools/)
10. [helm](https://helm.sh/docs/intro/quickstart/#install-helm)
11. [Postman CLI](https://learning.postman.com/docs/getting-started/installation/installation-and-updates/)
12. For cloud-specific tools, follow the instructions in the respective README file based on your provider.  
    Example for Azure: [terraform/azure/README.md](terraform/azure/README.md)

### Notes
- Existing files in the following locations will be backed up with a `.bak` extension, and the files will be overwritten:
    - `~/.config/rclone/rclone.conf`
    - `~/.kube/config`
- In the instructions below, `demo` is used as the environment name. You can replace it with your desired environment name, such as `dev`, `stage`, etc.

### Steps to Clone and Prepare

1. Clone the repository:a
     ```bash
     git clone https://github.com/Sanketika-labs/sunbird-ed-installer-fmps.git
     ```
2. Copy the template directory:
     ```bash
     cd terraform/<cloud-provider>   # Replace <cloud-provider> with your cloud provider (e.g., azure, aws, gcp)
     cp -r template demo
     cd demo
     ```
3. Fill in the variables in `demo/global-values.yaml`.
   take reference from  [terraform/azure/README.md]

4. Log in to your cloud provider:
    ```bash
    # If  cloud provider is Azure
    az login --tenant AZURE_TENANT_ID

    # If cloud provider is AWS
    aws configure

    # If cloud provider is GCP
    gcloud auth login
    ```
5. Based on cloud provider refer to the following for installation;
    - [GCP](terraform/gcp/README.md)
    - [Azure](terraform/azure/README.md])
    - [AWS](terraform/aws/README.md)

## Default Users in the Instance

This installation setup creates the following default users with different roles. You can update the passwords using the "Forgot Password" option or create new users using APIs.

| Role              | Email/User Name                  | Password             |
|-------------------|----------------------------------|----------------------|
| Admin             | admin-fmps@yopmail.com           | AdminFmps@123        |
| Content Creator   | contentcreator-fmps@yopmail.com  | CreatorFmps@123      |
| Content Reviewer  | contentreviewer-fmps@yopmail.com | ReviewerFmps@123     |
| Book Creator      | bookcreator-fmps@yopmail.com     | BookCreatorFmps@123  |
| Book Reviewer     | bookreviewer-fmps@yopmail.com    | BookReviewerFmps@123 |
| Public User 1     | user1@yopmail.com                | User1@123            |
| Public User 2     | user2@yopmail.com                | User2@123            |

## Upgrading Services

For any new implementations or updated image tags, upgrade the component using:
```bash
time ./install.sh install_component <building_block>
```
Replace <building_block> with the name of the building block in which updates are applied.

### Example: 
If the player tag is updated, please verify the corresponding building block from which the player service is deployed. In this case, the player service is deployed from the edbb building block.
```bash
time ./install.sh install_component edbb
```


##  Destorying the sunbird instance
```bash
cd terraform/<cloud-provider>/<env>
time ./install.sh destroy_tf_resources
```