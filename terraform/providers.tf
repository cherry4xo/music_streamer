terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">= 2.10.0"
    }
  }
}

provider "kubernetes" { }

provider "vault" {
  address = "http://vault-internal:8200"
  token = "root"
}