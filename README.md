
- Go to directory `src/txts_unit`

- Run the docker-compose
```
docker-compose up -d --build
```

- Make the `net_setup.sh` file executable
```
sudo chmod +x net_setup.sh
```

- Add the Open vSwitch network
```
./net_setup.sh
```

- To check log of a service
```
docker-compose logs -f <service_name>
```
`<service_name>` can be `hazelcast`, `hz_client`, `stamper` or `nginx`


- Send UDP packets on localhost port 8080
```
packetsender --num 10 -A  127.0.0.1 8080 "hello"
```
