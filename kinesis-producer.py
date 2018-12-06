#!/usr/bin/env python3

import argparse
import collections
import concurrent.futures
import functools
import itertools
import json
import logging
import time
import random
import string
import sys
import threading

import boto3
import botocore
import pyformance
import pyformance.reporters

kinesis = boto3.client('kinesis')
registry = pyformance.MetricsRegistry()

def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

# Source: https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def produce_records(minlength=1500, maxlength=2500):
    corpus = random_string(maxlength)
    while True:
        multiplier = 10 if random.random() < 0.05 else 1
        record_len = random.randint(minlength, maxlength) * multiplier

        yield {'Data': corpus[:record_len], 'PartitionKey': random_string(32)}

def put_record_producer(i, args):
    logger = logging.getLogger('Producer.%s' % i)
    logger.info('Starting up producer...')
    for records in grouper(produce_records(), args.batch_size):
        i = 0
        while True:
            try:
                with registry.timer('Latency').time():
                    res = kinesis.put_records(StreamName=args.stream, Records=records)

                if res['FailedRecordCount'] > 0:
                    registry.meter('Error/PartialCalls').mark(1)
                    registry.meter('Error/Records').mark(res['FailedRecordCount'])
                    records = list(map(lambda t: t[0], filter(lambda t: 'ErrorCode' in t[1], zip(records, res['Records']))))
                    with registry.timer('Backoff').time():
                        time.sleep(2**i + random.random())
                    i += 1
                    continue

                registry.meter('Success/Calls').mark(1)
                registry.meter('Success/Records').mark(len(records))
                registry.meter('Success/Bytes').mark(functools.reduce(lambda val,record: val + len(record['Data']) + len(record['PartitionKey']), records, 0))
            except botocore.exceptions.ClientError:
                registry.meter('Error/Calls').mark(1)
                registry.meter('Error/Records').mark(len(records))
                registry.meter('Error/Bytes').mark(functools.reduce(lambda val, record: val + len(record['Data']) + len(record['PartitionKey']), records, 0))
                continue
            break

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Script for benchmarking Kinesis producer strategies')
    parser.add_argument('-b', '--batch-size', type=int, default=1, help='Number of records to push with each API call')
    parser.add_argument('-d', '--debug', action="store_true", default=False, help='Print more information')
    parser.add_argument('-p', '--parallelism', type=int, default=1, help='The number of producers to run in parallel')
    parser.add_argument('-s', '--stream', type=str, help='The name fo the stream to write the data to', required=True)
    return parser.parse_args()

def main(args):
    wrapper = lambda i: put_record_producer(i, args)

    reporter = pyformance.reporters.ConsoleReporter(registry, 1)
    reporter.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        list(executor.map(wrapper, range(args.parallelism)))

    return 0

if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='[%(asctime)s][%(name)s] %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)

    logging.debug('Starting up. Args: %s', args)
    sys.exit(main(args))
