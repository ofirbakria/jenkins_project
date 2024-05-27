#!/bin/bash
set -e

# Start MongoDB in the background
mongod --replSet myReplicaSet --bind_ip localhost,mongo1 &

# Wait for MongoDB to start
echo "Waiting for MongoDB to start..."
sleep 10

# Initiate replica set
echo "Initiating replica set..."
mongosh --eval "rs.initiate({
  _id: 'myReplicaSet',
  members: [
    { _id: 0, host: 'mongo1' },
    { _id: 1, host: 'mongo2' },
    { _id: 2, host: 'mongo3' }
  ]
})"

wait