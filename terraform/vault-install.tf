resource "helm_release" "vault" {
  name = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart = "vault"
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