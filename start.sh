#!/bin/sh
if [ -z $NUM_ENGINES ] || [ $NUM_ENGINES -lt 1 ] || [ $NUM_ENGINES -gt 4 ];
then
    echo "NUM_ENGINES must be in range [1,4]."
    exit
fi
cd /work/marian-dev
/work/marian-dev/make-marian.sh 
/work/public-api/server_conf/make_nginx_load_balancer_conf.py $NUM_ENGINES
/work/public-api/server_conf/make_supervisord_conf.py $NUM_ENGINES
chmod 755 /etc/supervisor/conf.d/supervisord.conf
supervisord -c /etc/supervisor/conf.d/supervisord.conf &
nginx -g "daemon off;"
