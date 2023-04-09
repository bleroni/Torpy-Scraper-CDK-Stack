import boto3
import os

def lambda_handler(event, context):
    
    instance_id = os.environ.get("INSTANCE")
    
    script_path = '/home/ec2-user/main.py'
    
    ssm = boto3.client('ssm')
    ec2 = boto3.client('ec2')
    
    status = ec2.describe_instance_status(InstanceIds=[instance_id])["InstanceStatuses"]
    
    print(status[0]["InstanceState"]['Name'])

    if status[0]["InstanceState"]['Name'] != 'running':
        ec2.start_instances(InstanceIds=[instance_id])
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
    
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={
            'commands': [f'python3 {script_path}']
        }
    )
    
    print(response['Status'])
    
    ssm.close()
    ec2.close()