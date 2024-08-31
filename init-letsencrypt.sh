#!/bin/bash

# Run Certbot to obtain or renew the SSL/TLS certificate
certbot --nginx -d api.stories.williamcarter.dev

# Reload Nginx to apply the new certificate
nginx -s reload