resource "kubernetes_ingress_v1" "api_gateway_ingress" {
  metadata {
    name = "api-gateway-ingress"
    annotations = {
      "kubernetes.io/ingress.class": "nginx"
      "nginx.ingress.kubernetes.io/force-ssl-redirect": "true"
    }
  }

  spec {
    tls {
      hosts = ["api.music.cherry4xo.ru"]
      secret_name = "" # TODO paste tls secret
    }

    rule {
      host = "api.music.cherry4xo.ru"
      
      http {
        path {
          path = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.krakend.metadata[0].name

              port {
                number = 8080
              }
            }
          }
        }
      }
    }
  }
}