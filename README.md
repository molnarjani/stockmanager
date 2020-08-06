# stockmanager
App to track inventory of items in stock 

<details><summary>Architecture</summary>
<p>

https://miro.com/app/board/o9J_knlaMdQ=/

<img width="600" alt="architecture_diagram" src="https://github.com/molnarjani/stockmanager/blob/master/architecture_diagram.png?raw=true">

</p>
</details>


<details><summary>Database</summary>
<p>
<img width="600" alt="database_diagram" src="https://github.com/molnarjani/stockmanager/blob/master/dbdiagram.png?raw=true">

</p>
</details>


<details><summary>Setup steps</summary>
<p>

### First time setup
```
git clone git@github.com:molnarjani/stockmanager.git
cd stockmanager

# Setup docker network
docker network create kafka-network

# Setup Kafka
docker-compose -f docker-compose.kafka.yml up -d

# Sometimes broker likes to come up before `zookeeper` is ready, in that case:
docker-compose -f docker-compose.kafka.yml up -d zookeeper
# Wait a bit
docker-compose -f docker-compose.kafka.yml up -d broker

# Create environment file
cp sample.env .env

# Optional:
# Change the variables to your linking, eg: more secure passwords, better dbname, etc.
vi .env

# Setup database
docker-compose up -d db

# Start services
# Service depends on importer so it should bring that up as well
docker-compose up service
```

### Setup
```
docker-compose -f docker-compose.kafka.yml up -d
docker-compose up
```

### Try it in action
```
cd stockmanager
cp example.csv importer/input/.

# You should see something like this in service STDOUT
# service_1   | 2020-08-06 20:51:44 - root - INFO - increased item: 4-3, current amount: 4800
# service_1   | 2020-08-06 20:51:44 - root - INFO - increased item: 10-1, current amount: 800
# service_1   | 2020-08-06 20:51:44 - root - INFO - increased item: 5-12, current amount: 4800

# Check events topic
docker-compose -f docker-compose.kafka.yml exec broker kafka-console-consumer --bootstrap-server localhost:9092 --topic events --from-beginning

# Check errors topic (if there are any)
docker-compose -f docker-compose.kafka.yml exec broker kafka-console-consumer --bootstrap-server localhost:9092 --topic errors --from-beginning

# Check database
docker-compose exec db psql --user appuser -d appdata -c "select * from items order by id;"
```
</p>
</details>
