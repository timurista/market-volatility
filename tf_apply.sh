#!/bin/bash
export TF_VAR_GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN
echo $TF_GITHUB_ACCESS_TOKEN
cd infra
terraform init
export TF_VAR_GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN && terraform apply -auto-approve
