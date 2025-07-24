data "vault_generic_secret" "users_auth_secrets" {
  path = "secret/users-auth"
}

data "vault_generic_secret" "users_account_secrets" {
  path = "secret/users-account"
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
        service_account_name = kubernetes_service_account.app_sa[each.key].metadata[0].name

        image_pull_secrets {
          name = "gitlab-registry-secret"
        }

        volume {
          name = "tls-volume"
          secret {
            secret_name = kubernetes_secret.app_tls[each.key].metadata[0].name
          }
        }

        container {
          name = each.key
          image = "${var.ci_registry}/${var.ci_project_path}/${each.key}:${var.image_tag}"

          image_pull_policy = "Always"

          command = ["python3", "-u", "-m", "uvicorn", "main:app"]
          args = [
            "--host", "0.0.0.0",
            "--port", tostring(each.value.container_port),
            "--ssl-keyfile=/etc/tls/${each.key}.key",
            "--ssl-certfile=/etc/tls/${each.key}.crt",
            "--ssl-ca-certs=/etc/tls/ca.crt"
          ]

          port {
            container_port = each.value.container_port
          }

          volume_mount {
            name       = "tls-volume"
            mount_path = "/etc/tls"
            read_only  = true
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