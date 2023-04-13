import requests
import boto3
from bs4 import BeautifulSoup
import logging
import json
import botocore
import torpy
import os
from torpy.http.requests import tor_requests_session

from utils import (
    get_elements
)
from config import _BUCKET_

_PATH_TO_DATA_ = 'article_data.json' # s3 object key

_LINK_ = 'https://www.merrjep.com/shpalljet/imobiliare-vendbanime/toke-fusha-farma/lipjan' # link to be scraped
_PAGE_LINK_ = 'https://www.merrjep.com/shpalljet/imobiliare-vendbanime/toke-fusha-farma/lipjan?Page={}'
_ARTICLE_LINK_ = 'https://www.merrjep.com/shpallja/imobiliare-vendbanime/toke-fusha-farma/shitet/lipjan/{}' #use .format() with the article num to get the link to an article urn

logger = logging.getLogger(__name__)

f1 = '/home/ec2-user/.local/share/torpy/network_status'
f2 = '/home/ec2-user/.local/share/torpy/dir_key_certificates'

from time import sleep

class Scraper(object):

    def __init__(self, debug=False):

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        logging.getLogger("botocore").setLevel(logging.CRITICAL) #botocore logger has a lot to say
        logging.getLogger("torpy").setLevel(logging.INFO)
        self.logger = logger

        # upon instantiation, get data from s3
        self.get_data()


    def main(self):
        #check for new articles
        if self.article_data:
            new_articles = self.check_site()
        else:
            #if first time, scrape first 2000 results
            new_articles = self.check_pages(50)
        
        #send requests to new articles
        self.send_requests(new_articles)


    def check_pages(self, pages):
        index = 2
        new_articles = []
        while (len(new_articles) + len(self.article_data)) < 2000:
            try:
                with tor_requests_session() as s:
                    for i in range(index, pages):
                        if len(new_articles) >= 2000:
                            break

                        link = _PAGE_LINK_.format(i)
                        
                        #find new articles and add them to new_aricles
                        soup = BeautifulSoup(s.get(link).content, 'html.parser')
                        new_articles.extend([num for num in [listing.string.split("'")[1] for listing in soup.find('div', class_='result-content').findAll('script')] if num not in self.article_data])

                        self.logger.debug(f"{len(new_articles)} new articles")
                        
            except (torpy.circuit.CellTimeoutError, requests.exceptions.ConnectTimeout):
                # picks up where left off if failure
                index = i
        
        return new_articles
            
            
    def check_site(self):
        
        soup = BeautifulSoup(requests.get(_LINK_).content, 'html.parser')

        retrys = 0
        while retrys < 3:
            try:
                with tor_requests_session() as s:
                    soup = BeautifulSoup(s.get(_LINK_).content, 'html.parser')
                    break
    
            except (torpy.circuit.CellTimeoutError, requests.exceptions.ConnectTimeout):
                retrys += 1
        else:
            raise ValueError("Initial Request Failed")

        # get the return data from request
        listings = soup.find('div', class_='result-content').findAll('script')

        # get the articles' unique identifiers
        article_nums = [listing.string.split("'")[1] for listing in listings]
        
        # get articles not in data (new articles)
        new_articles = [num for num in article_nums if num not in self.article_data]

        #check first 3 pages for new articles
        self.check_pages(3)

        return new_articles
        
        
    def send_requests(self, new_articles):
        #WALRUS USE CASE!! iterates through articles, constantly removing checked articles, terminates loop when articles is empty (all articles checked)
        # this is needed instead of usual for loop, becuase when the connection inevitably fails and the exception is caught, it needs to keep running, hence while loop
        while (articles := [article for article in new_articles if article not in self.article_data]): 
            self.logger.debug(f"articles: {articles}")
            try:
                with tor_requests_session() as s: # try to get as many requests as possible out of one session, loading takes considerable time
                    self.logger.debug("Runngins")
                    
                    for article in articles:
    
                        link = _ARTICLE_LINK_.format(article)
                    
                        self.logger.info(f"Trying {article}")
                        
                        res = s.get(link)
                        self.article_data[article] = get_elements(BeautifulSoup(res.content, 'html.parser'))
                        self.logger.debug(f"{article}: {res.status_code}") # debugging
                        
                        if res.status_code != 200: # if connection is blocked, make new connections
                            self.logger.debug("Session Failed... Restarting")
                            break
        
            except (torpy.circuit.CellTimeoutError, requests.exceptions.ConnectTimeout):
                pass
      

    def get_data(self):
        """
        Updates class level data to stored data in s3
        """

        s3 = boto3.client('s3')

        try:
            res = s3.get_object(Bucket=_BUCKET_, Key=_PATH_TO_DATA_)
            self.article_data = json.loads(res['Body'].read().decode('utf-8'))
            
        # upon first launch, object wont be there
        except botocore.exceptions.ClientError as error:
            self.logger.debug(error)
            self.article_data = {}
        
        s3.close()


    def storeData(self):
        #updates s3 with current class level data

        if self.article_data:
            s3 = boto3.client('s3')

            s3.put_object(Bucket=_BUCKET_,
                    Key=_PATH_TO_DATA_,
                    Body=json.dumps(self.article_data,indent=4).encode('utf-8'),
                    ContentType='application/json'
                    )
            
            s3.close()


    # these enable with-as statement 
    # store data to s3 upon closing
    # e.g: with Scraper() as s:
    def close(self):
        self.storeData()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(exc_type)
        if exc_value:
            print(exc_value)
        if traceback:
            print(traceback)
        self.close()
        
        
if __name__ == '__main__':
    with Scraper(debug=True) as s:
        s.check_site()
