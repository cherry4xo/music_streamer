data "vault_generic_secret" "postgres_credentials" {
  path = "secret/data/platform/postgres"
}

data "vault_generic_secret" "redis_credentials" {
  path = "secret/data/platform/redis"
}

resource "helm_release" "postgres" {
  name = "postgres"
  chart = "./bitnami-charts/bitnami/postgresql"

  set = [
    {
      name  = "auth.postgresPassword"
      value = var.postgres_admin_password
    },
    {
      name  = "auth.databases[0]"
      value = var.auth_db_name
    },
    {
      name  = "auth.usernames[0]"
      value = var.auth_db_user
    },
    {
      name  = "auth.passwords[0]"
      value = var.auth_db_pass
    },
    {
      name  = "auth.databases[1]"
      value = var.account_db_name
    },
    {
      name  = "auth.usernames[1]"
      value = var.account_db_user
    },
    {
      name  = "auth.passwords[1]"
      value = var.account_db_pass
    }
  ]

  
}

resource "helm_release" "redis" {
  name       = "redis"
  chart = "./bitnami-charts/bitnami/redis"

  set = [
    {
      name  = "auth.password"
      value = tostring(var.redis_password)
    }
  ]
}

resource "helm_release" "kafka" {
    name = "kafka"
    chart = "./bitnami-charts/bitnami/kafka"
}