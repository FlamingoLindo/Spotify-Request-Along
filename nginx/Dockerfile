FROM nginx:1.19.7-alpine
RUN apk add bash

COPY --chown=nginx:nginx nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx default.conf /tmp/default.conf
COPY --chown=nginx:nginx start.sh /app/start.sh
# Mount or copy your SSL certs (commented out until you have certificates)
# COPY --chown=nginx:nginx certs/ /etc/nginx/certs/

WORKDIR /app
RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid && \
    mkdir -p /var/cache/nginx/proxy_cache && \
    chown -R nginx:nginx /var/cache/nginx/proxy_cache

USER nginx

CMD ["/bin/bash", "/app/start.sh"]