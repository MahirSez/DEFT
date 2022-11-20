
- Go to directory `src/txts_unit`

- To run the docker-compose
```
docker-compose up -d --build
```

- To check log of a service
```
docke-compose logs -f <service_name>
```
Service name can be `hazelcast`, `hz_client` or `nginx`


- Send packets on localhost port 8080
