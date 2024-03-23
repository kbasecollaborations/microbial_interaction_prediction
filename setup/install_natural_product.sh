#!/usr/bin/env bash

export PATH="/mambaforge/bin:$PATH"

# Set up natural product
mamba env create -f /deps/env_natural_product.yml
