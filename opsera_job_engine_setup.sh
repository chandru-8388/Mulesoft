#!/bin/bash
###############################################################################
# JOB-ENGINE SCRIPT IN OPSERA (paste into the Run Job / job-engine step)
# Installs Python + dependencies and runs the pipeline creation script.
###############################################################################

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y sudo python3-pip

python3 -m pip --version
pip install PyGithub requests

# Bearer token used by pipeline.py (set this as an Opsera secret/env var)
export GITHUB_TOKEN=<your_opsera_api_bearer_token>

# Repo folder that holds pipeline.py, template1.json, config1.json
cd GitRepoCreation

# Create the pipeline via the Opsera API
python3 pipeline.py
