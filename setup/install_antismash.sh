#!/usr/bin/env bash

mkdir -p /tmp
cd /tmp

apt-get update && apt-get -y install apt-transport-https gnupg

export PATH="/mambaforge/bin:$PATH"

mamba create -n antismash python=3.9
source activate antismash

mamba install -c bioconda -c conda-forge antismash=7.1.0
pip uninstall -y nrpys
pip install --no-input --upgrade-strategy only-if-needed nrpys

download-antismash-databases && antismash --prepare-data
