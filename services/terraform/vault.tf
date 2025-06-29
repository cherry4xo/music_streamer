resource "vault_auth_backend" "kubernetes" {
    type = "kubernetes"
}

resource "vault_kubernetes_auth_backend_config" "config" {
    backend = vault_auth_backend.kubernetes.path
    kubernetes_host = "https://kubernetes.default.svc"
    kubernetes_ca_cert = file("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
}

resource "vault_policy" "users_auth_policy" {
    name = "users-auth"
    policy = file("./hashicorp/users-auth-policy.hcl")
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
    policy = file("./hashicorp/users-account-policy.hcl")
}

resource "vault_kubernetes_auth_backend_role" "users_account_role" {
    backend = vault_auth_backend.kubernetes.path
    role_name = "users-account"
    bound_service_account_names = ["users-account-sa"]
    bound_service_account_namespaces = ["default"]
    token_policies = [vault_policy.users_account_policy.name]
    token_ttl = 3600
}