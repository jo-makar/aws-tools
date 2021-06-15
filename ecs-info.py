#!/usr/bin/env python3
# Get ecs cluster/service info

import boto3

import argparse
import json
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cluster')
    parser.add_argument('service', nargs='?')
    args = parser.parse_args()

    ecs_client = boto3.client('ecs')
    ec2_client = boto3.client('ec2')

    if args.service is None:
        services = []
        kwargs = {'cluster':args.cluster, 'maxResults':100}
        while True:
            resp = ecs_client.list_services(**kwargs)
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200
            services += resp['serviceArns']
            if not resp.get('nextToken'):
                break
            kwargs['nextToken'] = resp['nextToken']

        print(json.dumps(services, indent=2))

    else:
        tasks = []
        kwargs = {'cluster':args.cluster, 'serviceName':args.service, 'maxResults':100}
        while True:
            resp = ecs_client.list_tasks(**kwargs)
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200
            tasks += resp['taskArns']
            if not resp.get('nextToken'):
                break
            kwargs['nextToken'] = resp['nextToken']

        output = []
        for idx in range(0, len(tasks), 100):
            resp = ecs_client.describe_tasks(cluster=args.cluster, tasks=tasks[idx:idx+100])
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

            for task in resp['tasks']:
                assert len(task['containers']) == 1
                output += [{
                                  'task-arn': task['taskArn'],
                                'created-at': str(task['createdAt']),
                    'container-instance-arn': task['containerInstanceArn'],
                              'container-id': task['containers'][0]['runtimeId'],
                }]

        containers = [e['container-instance-arn'] for e in output]
        for idx in range(0, len(containers), 100):
            resp = ecs_client.describe_container_instances(cluster=args.cluster, containerInstances=containers[idx:idx+100])
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

            for cont in resp['containerInstances']:
                found = False
                for entry in output:
                    if entry['container-instance-arn'] == cont['containerInstanceArn']:
                        entry['ec2-instance'] = cont['ec2InstanceId']
                        found = True
                        break
                assert found

        instances = [e['ec2-instance'] for e in output]
        # Limit not specified in docs (ie 100 arbitrary here)
        for idx in range(0, len(instances), 100):
            resp = ec2_client.describe_instances(InstanceIds=instances)
            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

            for reservation in resp['Reservations']:
                for instance in reservation['Instances']:
                    found = False
                    for entry in output:
                        if entry['ec2-instance'] == instance['InstanceId']:
                            entry['private-ip'] = instance['PrivateIpAddress']
                            found = True
                            break

        for entry in output:
            del entry['container-instance-arn']

        print(json.dumps(output, indent=2))
