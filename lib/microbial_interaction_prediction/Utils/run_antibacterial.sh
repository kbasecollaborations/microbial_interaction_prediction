#!/usr/bin/env bash
outputs="$1"
no_SSN="$2"
# Read list of fasta files into a space-separated string
files=""
shift
shift

for file in "$@"; do
  files+=" $file"
done

export PATH="/mambaforge/bin:$PATH"
source activate natural_product
cd /deps/antibiotic-prediction
python multiple_predict_function.py   $files  --output_dir $outputs --no_SSN $no_SSN

