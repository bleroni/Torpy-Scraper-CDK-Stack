# CDK Stack for Web Scraper on EC2 with Lambda Function Trigger

This CDK Stack deploys a web scraper on an EC2 instance and a Lambda function that triggers the script every hour using an EventBridge trigger. The scraper script is written in Python and uses the TorPy library for anonymity.

## Scraper Script

The scraper script uses TorPy to create a tor-requests connection to check the main article page. It extracts the unique IDs provided by the website and uses those as the identifier in its data-store. After it finds new articles, it stores the number and visits each link through a tor connection. If the tor connection is rate limited or blocked, it will create a new tor connection. When the scraper visits each article, it extracts elements from the page. If any of the extractions fail, it returns false in the data. Upon scraper finish, it stores its data to s3.

## Resource Info

This cdk stack deploys an ec2 instance with the required scraper files, as well as a lambda function to trigger the scraper, and an event to trigger the lambda hourly. The scraper shuts off the instance once finished to save on costs, the lambda functionr re-activates it.

## Deployment Instructions

All necessary steps to installing and deploying this scraper. This is all made much simpler when deployed from aws cloud9.

### Prerequisites
- AWS CLI and CDK configured and installed
- note these come pre-installed in aws-cloud9

### Config
- open the "scraperstack.py" file
- change `_BUCKET_` to the appropriate value
- note the `key` variable, make an ec2 key-pair (.pem) with the same name value, keep the .pem file safe you'll need it later
- note you may aswell need to make a bucket

### Deployment
- Clone this repo and navigate into it
- run `pip install -r requirements.txt`
- run `cdk bootsrap`
- run `cdk deploy`

### Setup

After the main instance and the supporting infrastructre are deployed we have to set up some files on the ec2 instance

- ssh into the ec2 instance 
- `pip install -r requirements.txt`
- configure aws cli - run `aws configure`
- `crontab /tmp/cronjob`