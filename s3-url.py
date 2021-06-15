#!/usr/bin/env python3
# Create a s3-based time-limited url

import boto3

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bucket')
    parser.add_argument('path')
    parser.add_argument('--hours', '-o', type=int, default=24)
    args = parser.parse_args()

    kwargs = {'Params':{'Bucket':args.bucket, 'Key':args.path}, 'ExpiresIn':args.hours*3600}
    print(boto3.client('s3').generate_presigned_url('get_object', **kwargs))
    
