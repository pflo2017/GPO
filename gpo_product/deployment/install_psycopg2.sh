#!/bin/bash

# Install psycopg2 in the Docker container
ssh root@134.209.236.65 "docker exec gpo-app pip install psycopg2-binary" 