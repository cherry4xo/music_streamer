resource "helm_release" "vault" {
  name = "vault"
  chart = "./vault-helm"
  namespace = "default"

  values = [
    yamlencode({
      server = {
        dev = {
          enabled = true
        }
      }
    })
  ]
}