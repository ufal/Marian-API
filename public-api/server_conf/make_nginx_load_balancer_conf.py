#!/usr/bin/python3
import re
import sys

num_engines = int(sys.argv[1])
s = """
upstream aiohttp {
    @UNIX_DOMAIN_SERVERS
}

server {
    error_log /dev/stdout error;
    access_log /dev/stdout;
    listen 81;
    client_max_body_size 20M;
    add_header X-Request-ID $request_id; # Return to client
    # Set request timeout to 60 seconds
    proxy_read_timeout 60;
    proxy_connect_timeout 60;
    proxy_send_timeout 60;

    server_name marian-docker.com;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://aiohttp;
        proxy_set_header X-Request-ID $request_id; # Pass to app server
    }

}
"""
unix_domain_servers = ""
for i in range(1, num_engines + 1):
    unix_domain_servers += (
        "server unix:/tmp/marian_docker_{}.sock fail_timeout=0;\n\t".format(str(i))
    )

out = open("/etc/nginx/sites-enabled/nginx_load_balancer.conf", "w")
out.write(re.sub(r"@UNIX_DOMAIN_SERVERS", unix_domain_servers, s))
out.close()
