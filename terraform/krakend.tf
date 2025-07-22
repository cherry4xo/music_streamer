resource "kubernetes_deployment" "krakend" {
  metadata {
    name = "krakend-deployment"
  }
  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "krakend"
      }
    }

    template {
      metadata {
        labels = {
          app = "krakend"
        }
      }
      spec {
        volume {
          name = "krakend-tls-volume"
          secret {
            secret_name = kubernetes_secret.krakend_tls.metadata[0].name
          }
        }
        container {
          name = "krakend"
          image = "${var.ci_registry}/${var.ci_project_path}/krakend:${var.image_tag}"

          image_pull_policy = "Always"

          command = ["krakend", "run", "-d", "-c", "/etc/krakend/krakend.json"]

          volume_mount {
            name = "krakend-tls-volume"
            mount_path = "/etc/krakend/certs"
            read_only = true
          }

          port {
            container_port = 8080
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "krakend" {
  metadata {
    name = "krakend-service"
  }
  spec {
    selector = {
      app = kubernetes_deployment.krakend.spec[0].template[0].metadata[0].labels.app
    }
    port {
      protocol = "TCP"
      port = 8080
      target_port = 8080
      node_port = 30080
    }
    type = "NodePort"
  }
}