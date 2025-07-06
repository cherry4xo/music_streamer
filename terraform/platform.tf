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

    postgres_helm_values = [
      {
        name  = "auth.postgresPassword"
        value = var.postgres_admin_password
      }
    ]
  
    # Now, merge in the dynamic settings for each database, user, and password
    # The 'flatten' function is key here. It takes a list of lists and makes it a single flat list.
    postgres_db_settings = flatten([
      for key, config in local.postgres_configs : [
        {
          name  = "auth.databases[${key}]"
          value = config.db_name
        },
        {
          name  = "auth.usernames[${key}]"
          value = config.username
        },
        {
          name  = "auth.passwords[${key}]"
          value = config.password
        }
      ]
    ])
}

resource "helm_release" "postgres" {
    name = "postgres"
    chart = "./bitnami-charts/bitnami/postgresql"

    set = concat(
        local.postgres_helm_values,
        local.postgres_db_settings,
    )
}

resource "helm_release" "redis" {
    name = "redis"
    chart = "./bitname-charts/bitnami/redis"

    set = [
        {
            name = "auth.password"
            value = var.redis_password
        }
    ]
}

resource "helm_release" "kafka" {
    name = "kafka"
    chart = "./bitnami-charts/bitnami/kafka"
}