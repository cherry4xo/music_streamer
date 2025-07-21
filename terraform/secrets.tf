variable "postgres_admin_password" {
  description = "The password for the main PostgreSQL admin user"
  type = string
  sensitive = true
}

variable "redis_password" {
  description = "The password for the Redis instance"
  type = string
  sensitive = true
}

variable "auth_db_name" { type = string }
variable "auth_db_user" { type = string }
variable "auth_db_pass" { 
    type = string
    sensitive = true 
}

variable "account_db_name" { type = string }
variable "account_db_user" { type = string }
variable "account_db_pass" { 
    type = string
    sensitive = true 
}

resource "kubernetes_secret" "internal_ca" {
  metadata {
    name = "internal-ca-secret"
  }
  data = {
    "ca.crt" = file("./certs/ca.crt")
  }
}

resource "kubernetes_secret" "krakend_client_tls" {
  metadata {
    name = "krakend-client-tls-secret"
  }
  type = "kubernetes.io/rls"
  data = {
    "tls.crt" = file("./certs/krakend-client.crt")
    "tls.key" = file("./certs/krakend-client.key")
  }
}

resource "kubernetes_secret" "app_tls" {
  for_each = var.services

  metadata {
    name = "${each.key}-tls-secret"
  }
  type = "kubernetes.io/tls"
  data = {
    "tls.crt" = file("./certs/${each.key}.crt")
    "tls.key" = file("./certs/${each.key}.key")
  }
}