resource "kubernetes_service_account" "vault_auth_sa" {
    metadata {
        name = "vault-auth-sa"
        namespace = "default"
    }
}

data "kubernetes_secret" "vault_auth_token_secret" {
    metadata {
        name = "vault-auth-token"
        namespace = "default"
        annotations = {
          "kubernetes.io/service-account.name" = kubernetes_service_account.vault_auth_sa.metadata[0].name
        }
    }
    type = "kubernetes.io/service-account-token"
}

resource "vault_auth_backend" "kubernetes" {
    type = "kubernetes"
}

resource "vault_kubernetes_auth_backend_config" "config" {
    backend = vault_auth_backend.kubernetes.path
    kubernetes_host = "https://kubernetes.default.svc"
    token_reviewer_jwt = kubernetes_secret.vault_auth_token_secret.data.token
    kubernetes_ca_cert = base64decode(kubernetes_secret.vault_auth_token_secret.data["ca.crt"])
}

resource "vault_policy" "users_auth_policy" {
    name = "users-auth"
    policy = file("./services/platform/hashicorp/users-auth-policy.hcl")
}

resource "vault_kubernetes_auth_backend_role" "users_auth_role" {
    backend = vault_auth_backend.kubernetes.path
    role_name = "users-auth"
    bound_service_account_names = ["users-auth-sa"]
    bound_service_account_namespaces = ["default"]
    token_policies = [vault_policy.users_auth_policy.name]
    token_ttl = 3600
}

resource "vault_policy" "users_account_policy" {
    name = "users-account"
    policy = file("./services/platform/hashicorp/users-account-policy.hcl")
}

resource "vault_kubernetes_auth_backend_role" "users_account_role" {
    backend = vault_auth_backend.kubernetes.path
    role_name = "users-account"
    bound_service_account_names = ["users-account-sa"]
    bound_service_account_namespaces = ["default"]
    token_policies = [vault_policy.users_account_policy.name]
    token_ttl = 3600
}