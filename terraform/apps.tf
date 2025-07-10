data "vault_generic_secret" "users_auth_secrets" {
  path = "secret/data/users-auth"
}

data "vault_generic_secret" "users_account_secrets" {
  path = "secret/data/users-account"
}

resource "kubernetes_deployment" "app_deployments" {
  for_each = var.services

  metadata {
    name = "${each.key}-deployment"
    labels = { app = each.key }
  }

  spec {
    replicas = each.value.replicas
    selector {
      match_labels = { app = each.key }
    }
    template {
      metadata {
        labels = { app = each.key }
      }
      spec {
        service_account_name = kubernetes_service_account.app_sa[each.key].metadata.0.name

        container {
          name = each.key
          image = each.value.image

          port {
            container_port = each.value.container_port
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app_services" {
  for_each = var.services

  metadata {
    name = "${each.key}-service"
  }

  spec {
    selector = {
      app = each.key
    }
    port {
      protocol = "TCP"
      port = each.value.service_port
      target_port = each.value.container_port
    }

    type = "NodePort"
  }
}