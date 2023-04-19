# Bleron notes
https://github.com/Asilomare/Torpy-Scraper-CDK-Stack
git clone https://github.com/Asilomare/Torpy-Scraper-CDK-Stack/blob/main/scraper_script/main.py
Harrison Oliver
5:22 PM
git clone https://github.com/Asilomare/Torpy-Scraper-CDK-Stack
cd Torpy-Scraper-CDK-Stack


pip install requirements.txt
crontab /tmp/cronjob

cdk deploy


In Cloud9, create the key pair for the EC2 instance

# End of Bleron notes

# CDK Stack for Web Scraper on EC2

This CDK Stack deploys a web scraper on an EC2 instance and a Lambda function that triggers the script every hour using an EventBridge trigger. The scraper script is written in Python and uses the TorPy library for anonymity.

# Job Description

Simple website with no captcha-s.

Initially, 40 paginated pages that contain articles/listings have to be scraped, which contain about 2,000 articles/listings. After this, the script should check every hour for new articles.

This website publishes many times duplicated articles/listings, so the script has to check if the "new" article has already been scraped before.

Also, in case the data fields cannot be extracted from an article/listing, this has to be tracked somehow.

One technical issue that I have noticed is that when you click on a link in the website, sometimes it can remain on "loading" state and you cannot click other links. However, this is always resolved with a simple page reload.

All relevant data have to be saved on a AWS S3 bucket as JSON. However, I would be open to other suggestions, if they are more robust/efficient.

## Scraper Script

The scraper script uses TorPy to create a tor-requests connection to check the main article page. It extracts the unique IDs provided by the website and uses those as the identifier in its data-store. After it finds new articles, it stores the number and visits each link through a tor connection. If the tor connection is rate limited or blocked, it will create a new tor connection. When the scraper visits each article, it extracts elements from the page. If any of the extractions fail, it returns false in the data. Upon scraper finish, it stores its data to s3.

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
