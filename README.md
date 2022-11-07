# SportHackDays_H22

```
pip install faust
```

Execute python script with following command:
```
~/venv/sport_hack/bin/python3 test_faust_worker.py worker -l info --web-port=6066
```


Select environment where faust is installed:
```
~/venv/sport_hack/bin/python3
```


Select worker python script:
```
test_faust_worker.py
```

Start as worker:
```
worker
```

Print informations:
```
-l info
```

Set a unique port for each new worker:
```
--web-port=6066
```


### Data preparation
The timestamps had to be adjusted to a format like **2022-08-21 10:30:43.595+0100**. For this we have developed a simple python script.

Copy data to server:
```
scp -i .ssh/hslukey.sec projects/SportHackDays_H22/object_data_pp_P1.csv ubuntu@86.119.35.55:/home/ubuntu/hslu-dataplatform/data-transfer/hack-days-data/
```

### Create and visualize Stream

Log into ksql client:
```
docker exec -it ksqldb-cli ksql http://ksqldb-server-1:8088
```

Create a new stream -> first make sure that the old one is deleted.
```
DROP STREAM IF EXISTS centerOfGravity_s;
```

```
CREATE STREAM IF NOT EXISTS centerOfGravity_s 
  (time VARCHAR, 
   teams VARCHAR)
  WITH (kafka_topic='centerOfGravity',
        value_format='JSON');
```

```
SELECT * FROM centerOfGravity_s EMIT CHANGES;
```


### Start / Stop StreamSets Simulator from Commandline

1. On VM -> start bash in Streamset docker:
```
docker exec -it streamsets-1 bash
```

2. Insinde VM/StreamSetDocker -> Go to $SDC_DIST directory
```
cd /opt/streamsets-datacollector-3.22.2/
```

3. Start StreamSet Simulator
```
bin/streamsets cli -U http://localhost:18630 manager start -n Test55284d1b-15b1-4ed1-ad03-3097232af022
```

4. Stop StreamSet Simulator
```
bin/streamsets cli -U http://localhost:18630 manager stop -n Test55284d1b-15b1-4ed1-ad03-3097232af022
```


