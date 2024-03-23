#!/usr/bin/env bash

export PATH="/mambaforge/bin:$PATH"

# Set up RGI5
mamba env create -f /deps/env_rgi5.yml
