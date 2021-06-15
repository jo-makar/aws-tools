#!/usr/bin/env python3
# List autoscaling group ip addresses

import boto3

import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('autoscaling_group', metavar='autoscaling-group')
    args = parser.parse_args()

    ec2_client = boto3.client('ec2')

    output = []
    kwargs = {
        'Filters': [
            {'Name':'instance-state-name','Values':['pending','running']},
            {'Name':'tag:aws:autoscaling:groupName','Values':[args.autoscaling_group]},
        ],
        'MaxResults': 1000,
    }
    while True:
        resp = ec2_client.describe_instances(**kwargs)
        assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

        for reservation in resp['Reservations']:
            for instance in reservation['Instances']:
                output += [instance['PrivateIpAddress']]

        if not resp.get('NextToken'):
            break
        kwargs['NextToken'] = resp['NextToken']

    print(json.dumps(output, indent=2))
