Scripts for benchmarking throughput of different Kinesis producer batching & backoff strategies.

## Setup

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install boto3 pyformance
```

## Usage

```
$ ./kinesis-producer.py -h

usage: kinesis-producer.py [-h] [-b BATCH_SIZE] [-d] [-p PARALLELISM] -s
                           STREAM

Script for benchmarking Kinesis producer strategies

optional arguments:
  -h, --help            show this help message and exit
  -b BATCH_SIZE, --batch-size BATCH_SIZE
                        Number of records to push with each API call
  -d, --debug           Print more information
  -p PARALLELISM, --parallelism PARALLELISM
                        The number of producers to run in parallel
  -s STREAM, --stream STREAM
                        The name fo the stream to write the data to
```
