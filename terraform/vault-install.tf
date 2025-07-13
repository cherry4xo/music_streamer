resource "helm_release" "vault" {
  name = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart = "vault"
  version = "0.30.0"

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