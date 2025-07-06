terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">= 2.10.0"
    }
    vault = {
      source = "hashicorp/vault"
      version = ">= 5.0.0"
    }
    helm = {
      source = "hashicorp/helm"
      version = ">= 2.13.2"
    }
  }
}

provider "kubernetes" { 
  config_path    = "~/.kube/config"
  config_context = "music-streaming"
}

provider "helm" {
  kubernetes = {
    config_path    = "~/.kube/config"
    config_context = "music-streaming"
  }
}

provider "vault" { }