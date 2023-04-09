import boto3
import os

def lambda_handler(event, context):
    
    instance_id = os.environ.get("INSTANCE")
    
    script_path = '/home/ec2-user/main.py'
    
    ssm = boto3.client('ssm')
    
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunSheelScript',
        Parameters={
            'commands': [f'python3 {script_path}']
        }
        )
    
    ssm.close()
    
    return response