terraform {
  required_version = ">= 1.0"

  required_providers {
    docker = {
        source = "kreuzwerker/docker"
        version = "~> 3.0"
    }
  }
}

provider "docker" {
  
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "music-streaming"
}

resource "kubernetes_namespace" "music" {
  metadata {
    name = "music-streaming"
  }
}