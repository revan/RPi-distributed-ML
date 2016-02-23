# Distributed Sensor Network on Raspberry Pis

## Local Development
First install a couple packages:
```bash
apt-get install -y zookeeperd libzmq3-dev
```

To set up your local python environment:
```bash
sudo pip3 install virtualenv
virtualenv3 env
source env/bin/activate
pip install -r requirements.txt
```

The virtualenv ensures we all have the same packages installed. Remember to run `source env/bin/activate` in every new terminal.

First, start Zookeeper: 
```bash
sudo zkServer.sh start
```
I had to set up a config first:
```bash
sudo cp /etc/zookeeper/zoo_sample.cfg /etc/zookeeper/zoo.cfg
```

(For now, we need to tell zookeeper to delete its data at each run: from `zkCli.sh`, run `rmr /addr`)

Then start one terminal for each node. Source the virtualenv, then run your script, ex:
```bash
DEVICE_ID=1 python sample.py
```
incrementing `DEVICE_ID`.

(For now, need to uncomment a line in `Messager.getOwnAddr()`.)

## Deployment to Resin.io
The `Dockerfile` contains the instructions on how to provision the Pis.
Starting from a Raspbian image, it first installs the debian packages, then python, then copies over the repo and runs `init.sh`.

Push to the Resin.io repo and it will build any changes and deploy.

## Adding dependencies
If you ever add a python dependency, update `requirements.txt` like so:
```bash
pip freeze > requirements.txt
```

Debian and python packages also have to be added to the `Dockerfile`.
