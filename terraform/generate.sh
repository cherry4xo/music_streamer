#!/bin/bash
set -e

# --- Configuration ---
CERT_DIR="certs"
DAYS=3650

# --- Script Start ---
echo "--- Cleaning up old files in ${CERT_DIR} ---"
mkdir -p ${CERT_DIR}
rm -f ${CERT_DIR}/*.key ${CERT_DIR}/*.csr ${CERT_DIR}/*.crt ${CERT_DIR}/*.srl

# -------------------------------------------------------------------
# Phase 1: Create The Certificate Authority (CA)
# -------------------------------------------------------------------
echo "\n--- Phase 1: Creating the Certificate Authority (CA) ---"
openssl genrsa -out ${CERT_DIR}/ca.key 4096
openssl req -x509 -new -nodes -key ${CERT_DIR}/ca.key -sha256 -days ${DAYS} -out ${CERT_DIR}/ca.crt \
  -subj "/C=US/ST=California/L=San Francisco/O=MusicStreamer CA/CN=music-streamer-ca"
echo "--> CA created successfully."

# -------------------------------------------------------------------
# Generic function to create a server certificate
# -------------------------------------------------------------------
generate_server_cert() {
  local SERVICE_NAME=$1
  local COMMON_NAME_OVERRIDE=${2:-${SERVICE_NAME}-service.default.svc.cluster.local} # Allow overriding CN
  echo "\n--- Generating Server Certificate for '${SERVICE_NAME}' ---"

  # Generate private key
  openssl genrsa -out ${CERT_DIR}/${SERVICE_NAME}.key 2048

  # Generate temporary config with real service name and CN
  local TMP_CONF="${CERT_DIR}/openssl-${SERVICE_NAME}.cnf"
  sed -e "s/__CNF_SERVICE_NAME__/${SERVICE_NAME}/g" \
      -e "s/__CNF_COMMON_NAME__/${COMMON_NAME_OVERRIDE}/g" \
      openssl.cnf.template > ${TMP_CONF}

  # Generate CSR using the temporary config
  openssl req -new -key ${CERT_DIR}/${SERVICE_NAME}.key \
    -out ${CERT_DIR}/${SERVICE_NAME}.csr -config ${TMP_CONF}

  # Sign the CSR with the CA using the same temporary config
  openssl x509 -req -in ${CERT_DIR}/${SERVICE_NAME}.csr \
    -CA ${CERT_DIR}/ca.crt -CAkey ${CERT_DIR}/ca.key -CAcreateserial \
    -out ${CERT_DIR}/${SERVICE_NAME}.crt -days ${DAYS} -sha256 \
    -extfile ${TMP_CONF} -extensions v3_server

  # Verify SANs
  echo "--> Certificate for '${SERVICE_NAME}' is valid for the following hostnames:"
  openssl x509 -in ${CERT_DIR}/${SERVICE_NAME}.crt -noout -text | grep DNS

  # Clean up temporary config
  rm -f ${TMP_CONF}
}

# -------------------------------------------------------------------
# Phase 2: Generate Server Certificates
# -------------------------------------------------------------------
# For backend services
generate_server_cert "users-auth"
generate_server_cert "users-account"

# For the KrakenD Gateway itself
generate_server_cert "krakend" "krakend-gateway" # Use a distinct CN like 'krakend-gateway'

# -------------------------------------------------------------------
# Phase 3: Create Client Certificate for KrakenD (for mTLS)
# -------------------------------------------------------------------
echo "\n--- Phase 3: Creating the Client Certificate for KrakenD (for mTLS) ---"
openssl genrsa -out ${CERT_DIR}/krakend-client.key 2048
openssl req -new -key ${CERT_DIR}/krakend-client.key -out ${CERT_DIR}/krakend-client.csr \
  -subj "/C=US/ST=California/L=San Francisco/O=MusicStreamer/CN=krakend-client"
openssl x509 -req \
  -in ${CERT_DIR}/krakend-client.csr \
  -CA ${CERT_DIR}/ca.crt -CAkey ${CERT_DIR}/ca.key -CAcreateserial \
  -out ${CERT_DIR}/krakend-client.crt -days ${DAYS} -sha256 -extfile openssl.cnf.template -extensions v3_client

# -------------------------------------------------------------------
# Final Cleanup
# -------------------------------------------------------------------
echo "\n--- Cleaning up temporary CSR files ---"
rm -f ${CERT_DIR}/*.csr

echo "\n--- TLS/mTLS Certificate generation complete! ---"
echo "All files are located in the '${CERT_DIR}' directory."