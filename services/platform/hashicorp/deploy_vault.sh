#!/bin/bash

echo "Adding HashiCorp Heml repo..."
helm repo add hashicorp https://helm.releases.hashicorp.

echo "Installing Vault..."
helm install vault hashicorp/vault --set="server.dev.enabled=true"

echo "Vault installed successfully!"