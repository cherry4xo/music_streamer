#!/bin/bash

set -e

PROFILE="music"

# Check if Minikube is running, start it if not
if ! minikube status -p ${PROFILE} | grep -q "Running"; then
    echo "--------------------"
    echo "Starting Minikube..."
    echo "--------------------"
    minikube start --memory=6656 --cpus=4 --driver=docker -p ${PROFILE}
else
    echo "----------------------------"
    echo "Minikube is already running."
    echo "----------------------------"
fi

