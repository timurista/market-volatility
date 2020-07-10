#!/bin/bash
docker build --build-arg GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN} -f ./Dockerfile ./src -t github-cron
