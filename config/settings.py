from databricks.sdk.runtime import dbutils

# Pull the GCP credentials securely from Databricks Secrets
gcp_client_email = dbutils.secrets.get(scope="gcp_scope-flying-delays", key="client_email")
gcp_project_id = dbutils.secrets.get(scope="gcp_scope-flying-delays", key="project_id")
gcp_private_key = dbutils.secrets.get(scope="gcp_scope-flying-delays", key="private_key")
gcp_private_key_id = dbutils.secrets.get(scope="gcp_scope-flying-delays", key="private_key_id")