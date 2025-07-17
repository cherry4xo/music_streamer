resource "kubernetes_config_map" "krakend_config" {
  metadata {
    name = "krakend-config"
  }
  data = {
    "krakend.json" = file("${path.module}/../services/platform/krakend/config/partials/dev/settings.json")
  }
}

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
        container {
          name = "krakend"
          image = "devopsfaith/krakend:2.6"

          command = ["krakend", "run", "-c", "/etc/krakend/krakend.json"]

          port {
            container_port = 8080
          }

          volume_mount {
            name = "krakend-config-volume"
            mount_path = "/etc/krakend"
          }
        }

        volume {
          name = "krakend-config-volume"
          config_map {
            name = kubernetes_config_map.krakend_config.metadata[0].name
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