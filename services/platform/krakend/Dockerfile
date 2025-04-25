FROM krakend:2.9 as builder
ARG ENV=prod

COPY krakend.tmpl .
COPY config .

# Save temporary file to /tmp to avoid permission errors
RUN FC_ENABLE=1 \
    FC_OUT=/tmp/krakend.json \
    FC_PARTIALS="/etc/krakend/partials" \
    FC_SETTINGS="/etc/krakend/settings/$ENV" \
    FC_TEMPLATES="/etc/krakend/templates" \
    krakend check -d -t -c krakend.tmpl --lint

FROM krakend:2.9
# Keep operating system updated with security fixes between releases
RUN apk upgrade --no-cache --no-interactive

COPY --from=builder --chown=krakend:nogroup /tmp/krakend.json .
# Uncomment with Enterprise image:
# COPY LICENSE /etc/krakend/LICENSE

# Uncomment if you have certificates issued by a custom CA
# e.g., tls: failed to verify certificate: x509: certificate signed by unknown authority
#
# COPY yourca.pem /usr/local/share/ca-certificates/
# RUN update-ca-certificates
