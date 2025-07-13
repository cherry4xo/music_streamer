data "vault_generic_secret" "postgres_credentials" {
  path = "secret/data/platform/postgres"
}

data "vault_generic_secret" "redis_credentials" {
  path = "secret/data/platform/redis"
}

resource "helm_release" "postgres" {
  name = "postgres"
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
      name  = "auth.databases[0]"
      value = var.auth_db_name
      type = "string"
    },
    {
      name  = "auth.usernames[0]"
      value = var.auth_db_user
      type = "string"
    },
    {
      name  = "auth.passwords[0]"
      value = var.auth_db_pass
      type = "string"
    },
    {
      name  = "auth.databases[1]"
      value = var.account_db_name
      type = "string"
    },
    {
      name  = "auth.usernames[1]"
      value = var.account_db_user
      type = "string"
    },
    {
      name  = "auth.passwords[1]"
      value = var.account_db_pass
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
}