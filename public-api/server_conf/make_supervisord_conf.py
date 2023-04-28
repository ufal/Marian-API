#!/usr/bin/python3
import re
import sys

num_engines = sys.argv[1]
supervisord_conf = """
[supervisord]
environment=VERSION=%(ENV_VERSION)s,
            CHAR_LIMIT=%(ENV_CHAR_LIMIT)s,
            LINES_LIMIT=%(ENV_LINES_LIMIT)s,
nodaemon=true
logfile=/dev/null
logfile_maxbytes=0
[program:marian_docker]
numprocs = @NUM_ENGINES
numprocs_start = 1
process_name = example_%(process_num)s

command=/bin/bash -c "/work/public-api/start_marian_and_api.sh 80%(process_num)02d /tmp/marian_docker_%(process_num)s.sock"
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
autostart=true
user=www-data
autorestart=true
startretries=2
"""

out = open("/etc/supervisor/conf.d/supervisord.conf", "w")
out.write(re.sub(r"@NUM_ENGINES", num_engines, supervisord_conf))
out.close()
