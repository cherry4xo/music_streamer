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

  set = [
    {
      name  = "auth.postgresPassword"
      value = data.vault_generic_secret.postgres_credentials.data["admin_password"]
    },
    {
      name  = "auth.databases[0]"
      value = data.vault_generic_secret.postgres_credentials.data["auth_db_name"]
    },
    {
      name  = "auth.usernames[0]"
      value = data.vault_generic_secret.postgres_credentials.data["auth_db_user"]
    },
    {
      name  = "auth.passwords[0]"
      value = data.vault_generic_secret.postgres_credentials.data["auth_db_pass"]
    },
    {
      name  = "auth.databases[1]"
      value = data.vault_generic_secret.postgres_credentials.data["account_db_name"]
    },
    {
      name  = "auth.usernames[1]"
      value = data.vault_generic_secret.postgres_credentials.data["account_db_user"]
    },
    {
      name  = "auth.passwords[1]"
      value = data.vault_generic_secret.postgres_credentials.data["account_db_pass"]
    }
  ]

  
}

resource "helm_release" "redis" {
  name       = "redis"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis"
  version    = "18.6.0"

  set = [
    {
      name  = "auth.password"
      value = tostring(data.vault_generic_secret.redis_credentials.data["password"])
    }
  ]
}

resource "helm_release" "kafka" {
    name = "kafka"
    chart = "./bitnami-charts/bitnami/kafka"
}