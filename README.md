# File Medatata Extractor

This project is a Python application that handles file data extraction and synchronization. It uses PySpark for data processing and PostgreSQL for data storage.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.9
- PySpark
- PostgreSQL

### Installing

A step by step series of examples that tell you how to get a development environment running.

1. Clone the repository
2. Init app with 
```bash
make  init-db
```
3. Set up .env file (you can adjust number of synced files by changing NUM_FILES in .env file)

4. Run sync app with 
```bash
make start-worker-sync 
```
5. Run extract app with 
```bash
make start-worker-extract 
```


## Running the tests

```bash
make test
```

## Built With

* [Python](https://www.python.org/) - The programming language used
* [PySpark](https://spark.apache.org/docs/latest/api/python/) - Used for data processing
* [PostgreSQL](https://www.postgresql.org/) - Used for data storage

