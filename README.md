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

<details><summary>Services</summary>
<p>


  <details><summary>Importer</summary>
  <p>
  
  - Reads CSV files from input directory (mounted on host `<repo>/importer/input`)
  - Validates lines imported to schema, sends to Kafka `KAFKA_ERRORS_TOPIC` topic if the data does not match
  - Send data as JSON encoded as bytestring to Kafka `KAFKA_EVENTS_TOPIC` topic

  </p>
  </details>

  <details><summary>Service</summary>

  - Reads from on Kafka `KAFKA_EVENTS_TOPIC` topic
  - Increments or decrements (based on `event_type`, "sale" for decrement, "incoming" for increase) inventory items stored in `postgres` database
  - Logs events to a Transaction Journal in order to know which event was processed already
  - Retries events if `event` is `sale` type and item is not existing or amount would be less than 0, in hopes the events for `incoming` items are incoming (:D) but sale events arrived earlier, # of retries is controlled by `KAFKA_EVENT_RETRIES`
  - Pushes event to `KAFKA_ERRORS_TOPIC` topic if `KAFKA_EVENT_RETRIES` are exceeded
  <p>

  </p>
  </details>
</p>
</details>


<details><summary>TODOs</summary>
<p>
  
- [ ] Add unittest
- [ ] Share kafka_proucers.py, kafka_consumers.py, event schemas, most constants between services to make code MORE dry
- [ ] E2E tests
- [ ] Add UI(eg: some webapp) over `postgres` db with search capabilities so its usable by humanoids
- [ ] Add service to watch error topic and alert on specified error events (eg: item ran out of stock)
</p>
</details>
