from aws_cdk import (
    aws_lambda as _lambda,
    aws_events as events,
    aws_iam as iam,
    aws_s3 as s3,
    aws_events_targets as targets,
    App, Stack, Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_s3_assets as s3_assets
)
from constructs import Construct

_BUCKET_ = 'testbucketq3u4y397' # name of bucket
key = "test-key" # key name for ec2 instance ssh, file needs to be in docker

class ScraperstackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = s3.Bucket.from_bucket_name(self, _BUCKET_, "internalbucketname")
        
        vpc = ec2.Vpc(self, "MyVpc",
            nat_gateways=1
            )
            
        ast1 = s3_assets.Asset(self, "main_asset", path="scraper/scraper_script/main.py")
        ast2 = s3_assets.Asset(self, "utils_asset", path="scraper/scraper_script/utils.py")
        
        init = ec2.CloudFormationInit.from_elements(
            ec2.InitFile.from_existing_asset("/home/ec2-user/main.py", ast1),
            ec2.InitFile.from_existing_asset("/home/ec2-user/utils.py", ast2)
        )
        
        instance = ec2.Instance(self, "scraperInstance",
            vpc=vpc,
            instance_name="scraperInstance",
            instance_type=ec2.InstanceType(instance_type_identifier="t2.nano"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            key_name=key,
            user_data=ec2.UserData.for_linux(),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC),
            init=init
        )
        
        with open("scraper/scraper_script/requirements.txt", 'r') as f:
            requirements = f.read()
            
        instance.user_data.add_commands(
            'yum update -y',
            'sudo yum groupinstall "Development Tools" -y',
            'sudo yum install -y python38 python38-pip',
            'sudo python3 -m pip install --upgrade pip',
            f'echo "{requirements}" > /home/ec2-user/requirements.txt',
            f'echo \'_BUCKET_="{_BUCKET_}"\' > /home/ec2-user/config.py',

            'sudo service crond start',
            'sudo echo "0 * * * * python3 /home/ec2-user/main.py" > /tmp/cronjob',
            'sudo echo "0 * * * * python3 /home/ec2-user/main.py >> /home/ec2-user/myjob.log 2>&1" > /tmp/cronjob',
            "crontab /tmp/cronjob",
        )
        
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(22))
        bucket.grant_read_write(instance)