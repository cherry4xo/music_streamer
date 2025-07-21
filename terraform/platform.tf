data "vault_generic_secret" "postgres_credentials" {
  path = "secret/platform/postgres"
}

data "vault_generic_secret" "redis_credentials" {
  path = "secret/platform/redis"
}

locals {
  postgres_instances = {
    "auth" = {
      release_name = "postgres-auth"
      db_name      = var.auth_db_name
      db_user      = var.auth_db_user
      db_pass      = var.auth_db_pass
    },
    "account" = {
      release_name = "postgres-account"
      db_name      = var.account_db_name
      db_user      = var.account_db_user
      db_pass      = var.account_db_pass
    }
  }
}

# ... rest of the file ...

resource "helm_release" "postgres_instances" {
  for_each = local.postgres_instances

  name = each.value.release_name
  repository = "https://charts.bitnami.com/bitnami"
  chart = "postgresql"
  version = "13.2.27"

  set_sensitive = [
    {
      name  = "auth.postgresPassword"
      value = var.postgres_admin_password
      type = "string"
    },
    {
      name  = "auth.database"
      value = each.value.db_name
      type = "string"
    },
    {
      name  = "auth.username"
      value = each.value.db_user
      type = "string"
    },
    {
      name  = "auth.password"
      value = each.value.db_pass
      type = "string"
    }
  ]

  
}

resource "helm_release" "redis" {
  name       = "redis"
  repository = "https://charts.bitnami.com/bitnami"
  chart = "redis"
  version = "18.6.0"

  set_sensitive = [
    {
      name  = "auth.password"
      value = var.redis_password
      type = "string"
    }
  ]
}

resource "helm_release" "kafka" {
  name = "kafka"
  repository = "https://charts.bitnami.com/bitnami"
  version    = "26.3.1"
  chart      = "kafka"

  set = [
    {
      name  = "listeners.client.protocol"
      value = "PLAINTEXT"
    },
    {
      name  = "advertisedListeners"
      # This tells the brokers to advertise their internal Kubernetes DNS name.
      # The `{{ .Service.Name }}` is a Helm template value that resolves to the correct service name.
      value = "CLIENT://{{ .Service.Name }}.default.svc.cluster.local:9092"
    },
    {
      # This maps the internal listener name to the protocol.
      name = "listenerSecurityProtocolMap"
      value = "CLIENT:PLAINTEXT"
    }
  ]
}