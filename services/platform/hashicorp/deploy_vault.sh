KUBE_HOST="https://kubernetes.default.svc"
KUBE_CA_CERT=$(kubectl config view --raw -o jsonpath='{.clusters[?(@.name=="minikube")].cluster.certificate-authority-data}' | base64 --decode)
KUBE_CA_CERT_CONTENT=$(cat /home/cherry4xo/.minikube/ca.crt)

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

helm install vault hashicorp/vault --set "server.dev.enabled=true"

kubectl apply -f ./services/platform/hashicorp/serviceaccountauth.yaml

kubectl port-forward vault-0 8200:8200 &

VAULT_SA_TOKEN=$(kubectl create token vault-auth --namespace default --duration 8760h)

vault auth enable kubernetes

vault write auth/kubernetes/config \
    token_reviewer_jwt="$VAULT_SA_TOKEN" \
    kubernetes_host="$KUBE_HOST" \
    kubernetes_ca_cert="$KUBE_CA_CERT_CONTENT"