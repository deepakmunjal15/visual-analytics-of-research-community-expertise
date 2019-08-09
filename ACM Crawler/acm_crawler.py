# -*- coding: utf-8 -*-

#Install Libraries
from bs4 import BeautifulSoup
import urllib2
import re
import csv
import itertools

#Add path to the file test.csv
writer=csv.writer(open('Path to crawled speaker data.csv','wb'))
x=[]
html = urllib2.urlopen("https://speakers.acm.org/")
soup = BeautifulSoup(html)
for h in soup.findAll("div", {"id": "topics-list"}):
  for a in h.findAll("a", {"href": True}):
    x.append("https://speakers.acm.org"+a["href"])

#https://speakers.acm.org/topics/applied-computing type page
for i in range(len(x)):
    html = urllib2.urlopen(x[i])
    soup = BeautifulSoup(html)
    for link in soup.findAll('a', attrs={'href': re.compile("\.\./speakers/")}):
        a=link.get('href')
        a=a.replace("..", "http://speakers.acm.org")
        a=(re.sub(r"\s+", "", a))
        a=a.encode('utf-8')
        a=a.replace("ö", "o")
        
        #Speaker page
        try:
            html = urllib2.urlopen(a)
        except urllib2.HTTPError as e:
            if e.getcode() == 404:
                continue
            raise
            
        #Using beautiful soup to crawl data
        soup = BeautifulSoup(html)
        for h in soup.findAll("li", {"class": "current"}):
            speaker_name=h.text
            speaker_name=speaker_name.encode('utf-8')
            writer.writerow([speaker_name])
            
        for h in soup.findAll("div", {"class": "speakers"}):
            for a in h.findAll("span"):
                b=a.text
                speaker_loc=re.sub(r"\s*Based in\s*", "", str(b))
                speaker_loc=re.sub(r"\s*$", "", str(speaker_loc))
                writer.writerow([speaker_loc])
                break