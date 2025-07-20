resource "kubernetes_config_map" "krakend_config" {
  metadata {
    name = "krakend-config"
  }
  data = {
    "krakend.tmpl" = file("../services/platform/krakend/krakend.tmpl")
    "config--partials--dev--settings.json" = file("../services/platform/krakend/config/partials/dev/settings.json")
    "endpoints---auth.json" = file("/..services/platform/krakend/endpoints/auth.json")
    "endpoints---account.json" = file("../services/platform/krakend/endpoints/account.json")
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
          image = "${var.ci_registry}/${var.ci_project_path}/kranend:${var.image_tag}"

          command = ["krakend", "run", "-d", "-c", "/etc/krakend/krakend.tmpl"]
          
          port {
            container_port = 8080
          }

          volume_mount {
            name = "krakend-config-volume"
            mount_path = "/etc/krakend/krakend.tmpl"
            sub_path = "krakend.tmpl"
          }
          volume_mount {
            name = "krakend-config-volume"
            mount_path = "/etc/krakend/config/partials/dev/settings.json"
            sub_path = "config--partials--dev--settings.json"
          }
          volume_mount {
            name       = "krakend-config-volume"
            mount_path = "/etc/krakend/endpoints/auth.json"
            sub_path   = "endpoints---auth.json"
          }
          volume_mount {
            name       = "krakend-config-volume"
            mount_path = "/etc/krakend/endpoints/account.json"
            sub_path   = "endpoints---account.json"
          }

          env {
            name = "FC_SETTINGS"
            value = "/etc/krakend/config/partials/dev"
          }
          env {
            name = "FC_ENABLE"
            value = 1
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