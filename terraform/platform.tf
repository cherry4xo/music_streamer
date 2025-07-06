locals {
    postgres_configs = {
        "auth" = {
            db_name = var.auth_db_name
            username = var.auth_db_user
            password = var.auth_db_pass
        },
        "account" = {
            db_name = var.account_db_name
            username = var.account_db_user
            password = var.account_db_pass
        }
    }
}

resource "helm_release" "postgres" {
    name = "postgres"
    repository = "https://charts.bitnami.com/bitnami"
    chart = "postgresql"
    version = "13.2.27"

    dynamic "set" {
      for_each = local.postgres_configs
      content {
        name = "auth.databases[${iterator.key}]"
        value = set.value.db_name
      }
    }

    dynamic "set" {
      for_each = local.postgres_configs
      content {
        name = "auth.usernames[${iterator.key}]"
        value = set.value.username
      }
    }

    dynamic "set" {
      for_each = local.postgres_configs
      content {
        name = "auth.passwords[${iterator.key}]"
        value = set.value.password
      }
    }

    set {
      name = "auth.postgresPassword"
      value = set.postgres_admin_password
    }
}

resource "helm_release" "redis" {
    name = "redis"
    repository = "https://charts.bitnami.com/bitnami"
    chart = "redis"
    version = "18.6.0"

    set {
        name = "auth.password"
        value = var.redis_password
    }
}

resource "helm_release" "kafka" {
    name = "kafka"
    repository = "https://charts.bitnami.com/bitnami"
    chart = "kafka"
    version = "26.3.1"
}