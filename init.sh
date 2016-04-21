#!/bin/sh

echo "Boot complete."
echo "I am device #$DEVICE_ID"

echo "Launching Zookeeper"
service zookeeper stop
echo $DEVICE_ID > /var/lib/zookeeper/myid
service zookeeper start

echo "Starting averaging"
python3 /app/avg_sync.py
