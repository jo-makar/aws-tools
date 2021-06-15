#!/usr/bin/env python3
# Get ec2 instance info

import boto3

import json
import os.path
import pickle
import time

if __name__ == '__main__':
    # Internally cache the results to support quickly filtering results with repeated calls (say with jq)
    path = os.path.join(os.path.dirname(__file__), os.path.splitext(os.path.basename(__file__))[0] + '.pickle')
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 3600:
        with open(path, 'rb') as file:
            responses = pickle.load(file)

    else:
        ec2_client = boto3.client('ec2')
        responses = []
        kwargs = {
               'Filters': [ {'Name':'instance-state-name','Values':['pending','running']} ],
            'MaxResults': 1000,
        }
        while True:
            resp = ec2_client.describe_instances(**kwargs)
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200
            responses += [resp]
            if not resp.get('NextToken'):
                break
            kwargs['NextToken'] = resp['NextToken']

        with open(path, 'wb') as file:
            pickle.dump(responses, file)

    def name(instance):
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                return tag['Value']
        return None

    output = []
    for resp in responses:
        for reservation in resp['Reservations']:
            for instance in reservation['Instances']:

                output += [{
                            'id': instance['InstanceId'],
                           'key': instance.get('KeyName'),
                      'launched': str(instance['LaunchTime']),
                    'avail-zone': instance['Placement']['AvailabilityZone'],
                    'private-ip': instance['PrivateIpAddress'],
                     'public-ip': instance.get('PublicIpAddress'),
                        'subnet': instance['SubnetId'],
                           'vpc': instance['VpcId'],
                          'name': name(instance),
                }]

        print(json.dumps(output, indent=2))
