#!/bin/bash

# Check if the .env file exists
if [ -f .env ]; then
    # Load environment variables from the .env file
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
fi
# Set the working directory to the current directory
export WORKDIR=$(pwd)
# Add the working directory to the PYTHONPATH
export PYTHONPATH="$WORKDIR:$PYTHONPATH"
# python ./notebook/test_milvus_connect.py
# python ./notebook/test_embeddings.py
# python ./notebook/test_gpt.py
# python ./notebook/test_ingest.py
# python ./notebook/drop_mongodb.py
# python ./notebook/test_query.py
# python ./notebook/delete_milvus_collection.py
# python ./notebook/check_mongo.py
# python ./notebook/test_mongo_connect.py
# python ./notebook/check_connect.py
# python ./notebook/test_structure.py
# python ./src/sort_mongo/sort.py
# python ./src/api/test.py
# python ./notebook/test_search.py
# python ./src/llms/gemini.py
# python ./notebook/test_search.py
# python ./notebook/test_gemini.py
python ./notebook/test_full_query.py