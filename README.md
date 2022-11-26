
- Go to directory `src/txts_unit`

- To run the docker-compose
```
docker-compose up -d --build
```

- To check log of a service
```
docker-compose logs -f <service_name>
```
`<service_name>` can be `hazelcast`, `hz_client` or `nginx`


- Send UDP packets on localhost port 8080
