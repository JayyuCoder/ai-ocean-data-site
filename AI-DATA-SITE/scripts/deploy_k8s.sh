#!/usr/bin/env bash
# Apply Kubernetes manifests in deploy/k8s
set -euo pipefail

DIR=$(cd "$(dirname "$0")/.." && pwd)
kubectl apply -f "$DIR/deploy/k8s/"

echo "Kubernetes manifests applied. Ensure your kubeconfig is set and image is available." 
