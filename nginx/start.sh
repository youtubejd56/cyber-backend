#!/bin/sh
set -e

# substitute BACKEND_HOST/BACKEND_PORT into nginx config template
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# start nginx in foreground
exec nginx -g 'daemon off;'
