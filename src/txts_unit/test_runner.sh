set -xe
docker-compose down
docker-compose up -d
sleep 30
bash net_setup.sh
packetsender --num 1000 --rate 100000 -A 127.0.0.1 8080 "hello"