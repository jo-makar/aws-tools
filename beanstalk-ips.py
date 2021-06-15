#!/usr/bin/env python3
# List beanstalk ip addresses

import boto3

import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('beanstalk')
    args = parser.parse_args()

    ebs_client = boto3.client('elasticbeanstalk')
    ec2_client = boto3.client('ec2')

    resp = ebs_client.describe_environment_resources(EnvironmentName=args.beanstalk)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200
    instance_ids = [i['Id'] for i in resp['EnvironmentResources']['Instances']]

    output = []
    kwargs = {
        'InstanceIds': instance_ids,
            'Filters': [ {'Name':'instance-state-name','Values':['pending','running']} ],
    }
    resp = ec2_client.describe_instances(**kwargs)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    for reservation in resp['Reservations']:
        for instance in reservation['Instances']:
           output += [instance['PrivateIpAddress']]

    print(json.dumps(output, indent=2))
