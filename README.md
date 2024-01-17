# C2C view count benchmark

A project to check the time required by a pg dbsm to perform variable amount of bulk updates on a `view_count` field.

See https://github.com/c2corg/v6_api/pull/1726

## Setup
````
  // Create a new virtual env 
  python3 -m venv .venv
  
  // Allow using python and pip cli from virtual env in the terminal
  source ./.venv/bin/activate 
  
  // Install dependencies 
  pip install -r requirements.txt  
  
  // Start Redis and PostgreSQL
  docker compose up -d
  
  // Create column view_count with default value set to 0 in documents table
  make setup
````

## Run
````
.venv/bin/python main.py 10000 <-- where 10000 is the amount of docs to update  
    
````
... and check the result logs in the terminal, the time required for each query will be displayed using sqlalchemy
[query profiling](https://docs.sqlalchemy.org/en/13/faq/performance.html#query-profiling).

Each bulk update query will update 4000 documents max by default. So if you specify an amount of docs > 4000 it will be 
divided into several bulk update query that will update 4000 documents max. You can change this default value in 
[this file](https://github.com/florentcadot/c2c-update-view-counter-benchmark/blob/master/main.py)   
