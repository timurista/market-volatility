#!/bin/bash
echo "USING TOKEN $GITHUB_ACCESS_TOKEN"
docker run -d --restart unless-stopped -e GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN github-cron:latest
