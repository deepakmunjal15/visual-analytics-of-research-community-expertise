
#Libraries to install
from flask import Flask, render_template, request, jsonify
import os
import re
import random
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from collections import OrderedDict
import json
import pandas as pd
from urllib2 import urlopen

#Reading data files
def read():
    dataSetPath="Path to Speakers.csv"
    df = pd.read_csv(dataSetPath)
    matrix2 = df.as_matrix()
    return matrix2

def read1():
    dataSetPath="Path to 2018-03 Requests for the past Year.csv"
    df = pd.read_csv(dataSetPath)
    matrix2 = df.as_matrix()
    return matrix2

#searching speaker names
def search(name, radio_option):
    loc_array=[]
    desc=[]
    if radio_option=="a":
        all_data=read()
        pattern = re.compile(name, re.IGNORECASE)
        for i in range(len(all_data)):
            if re.search(pattern, all_data[i][0]):
                desc.append(str("Lecturer:"+all_data[i][0])+"<br />"+"Lecturer Email:"+str(all_data[i][1])+"<br />"+"City:"+str(all_data[i][2])+"<br />"+"State:"+str(all_data[i][3])+"<br />"+"Lecturer Country:"+str(all_data[i][4])+"<br />"+"Employer:"+str(all_data[i][5])+"<br />"+"Employer Type:"+str(all_data[i][6])+"<br />"+"Name of Nominator:"+str(all_data[i][7])+"<br />"+"Referred by:"+str(all_data[i][8])+"<br />"+"Num. Lectures:"+str(all_data[i][9])+"<br />"+"Last Updated:"+str(all_data[i][10])+"<br />"+"Accepted Date:"+str(all_data[i][11])+"<br />"+"Expire Date:"+str(all_data[i][12])+"<br />"+"Client No.:"+str(all_data[i][13])+"<br />"+"Awards:"+str(all_data[i][14])+"<br />"+"Featured Speaker:"+str(all_data[i][15]))
                loc=str(all_data[i][2])+","+str(all_data[i][3])+","+str(all_data[i][4])
                loc=loc.replace("nan", "")
                loc=(re.sub(r"\s+", "", loc))
                loc=loc.replace(",,", ",")
                loc_array.append(loc)
                
    elif radio_option=="b":
        all_data=read1()
        pattern = re.compile(name, re.IGNORECASE)
        for i in range(len(all_data)):
            if re.search(pattern, all_data[i][1]):
                desc.append(str(all_data[i][1])+"<br />"+str(all_data[i][2])+"<br />"+str(all_data[i][3])+"<br />"+str(all_data[i][4])+"<br />"+str(all_data[i][5])+"<br />"+str(all_data[i][6])+"<br />"+str(all_data[i][7])+"<br />"+str(all_data[i][8])+"<br />"+str(all_data[i][9])+"<br />"+str(all_data[i][10])+"<br />"+str(all_data[i][11])+"<br />"+str(all_data[i][12])+"<br />"+str(all_data[i][13])+"<br />"+str(all_data[i][14])+"<br />"+str(all_data[i][15])+"<br />"+str(all_data[i][16]))
                loc=str(all_data[i][12])+","+str(all_data[i][13])+","+str(all_data[i][14])
                loc=loc.replace("nan", "")
                loc=(re.sub(r"\s+", "", loc))
                loc=loc.replace(",,", ",")
                loc_array.append(loc)
    
    return loc_array, desc

#Converting location into lat log
def getlatlon(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    url += "address=+%s&key=Add a key here" % (location)
    v = urlopen(url).read()
    j = json.loads(v)
    t=re.findall(ur"u'location'\s*:\s*{\s*u'lat'\s*:\s*(-?\d+\.\d+),\s*u'lng'\s*:\s*(-?\d+\.\d+)\s*}", str(j))
    return t

#searching topics
def search1(topic):
    loc_array=[]
    desc=[]
    all_data=read1()
    pattern = re.compile(topic, re.IGNORECASE)
    for i in range(len(all_data)):
        if re.search(pattern, all_data[i][7]):
            
            desc.append(str("Lecturer:"+all_data[i][1])+"<br />")
            
            
            loc=str(all_data[i][12])+","+str(all_data[i][13])+","+str(all_data[i][14])
            loc=loc.replace("nan", "")
            loc=(re.sub(r"\s+", "", loc))
            loc=loc.replace(",,", ",")
            loc_array.append(loc)
    return loc_array, desc

#searching between Years
def search2(year_from, year_to):
    year_from=int(year_from)
    year_to=int(year_to)
    year_to=year_to+1
    loc_array=[]
    desc=[]
    all_data=read1()
    for year in range(year_from, year_to):
        year=str(year)
        pattern = re.compile(year, re.IGNORECASE)
        for i in range(len(all_data)):
            if re.search(pattern, all_data[i][9]):
                desc.append(str(all_data[i][1])+"<br />"+str(all_data[i][2])+"<br />"+str(all_data[i][3])+"<br />"+str(all_data[i][4])+"<br />"+str(all_data[i][5])+"<br />"+str(all_data[i][6])+"<br />"+str(all_data[i][7])+"<br />"+str(all_data[i][8])+"<br />"+str(all_data[i][9])+"<br />"+str(all_data[i][10])+"<br />"+str(all_data[i][11])+"<br />"+str(all_data[i][12])+"<br />"+str(all_data[i][13])+"<br />"+str(all_data[i][14])+"<br />"+str(all_data[i][15])+"<br />"+str(all_data[i][16]))
                loc=str(all_data[i][12])+","+str(all_data[i][13])+","+str(all_data[i][14])
                loc=loc.replace("nan", "")
                loc=(re.sub(r"\s+", "", loc))
                loc=loc.replace(",,", ",")
                loc_array.append(loc)
    
    return loc_array, desc


#Using Flask Framework
app = Flask(__name__)

global splitPercent, lower, punc, number, style, data_s, arr
splitPercent=0
data_s=[]
arr=0

@app.route('/',methods = ['POST', 'GET'])
def get_form_data():
    lat_array=[]
    long_array=[]
    desc=[]
    numbers=[]
    
#Capture distribution from html form
    radio_option="a"
    distribution = request.form.get('distribution')
    if distribution!=None and distribution!= False and distribution!= "":
        radio_option=distribution
    
#Capture speaker_name from html form
    speaker_name=request.form.get('speaker_name')
    if speaker_name!=None and speaker_name!= False:
        lat_array=[]
        long_array=[]
        desc=[]
        loc_array, desc=search(speaker_name, radio_option)
        for i in range(len(loc_array)):
            x=getlatlon(loc_array[i])
            lat_array.append(float(x[0][0]))
            long_array.append(float(x[0][1]))
        
        numbers=range(len(desc))
    
#Capture topic from html form
    topic=request.form.get('topic')
    if topic!=None and topic!= False and topic!= "":
        
        lat_array=[]
        long_array=[]
        desc=[]
        loc_array, desc=search1(topic)
    
        for i in range(len(loc_array)):
            x=getlatlon(loc_array[i])
            lat_array.append(float(x[0][0]))
            long_array.append(float(x[0][1]))
        
        numbers=range(len(desc))
    
#Capture years from html form
    year_from=request.form.get('year_from')
    year_to=request.form.get('year_to')
    if year_from!=None and year_from!= False and year_from!= "" and year_to!=None and year_to!= False and year_to!= "":
        lat_array=[]
        long_array=[]
        desc=[]
        loc_array, desc=search2(year_from, year_to)
    
        for i in range(len(loc_array)):
            x=getlatlon(loc_array[i])
            lat_array.append(float(x[0][0]))
            long_array.append(float(x[0][1]))
        
        numbers=range(len(desc))

#Rendering back data in the html form
    return render_template('a2.html', value1=desc, value2=lat_array, value3=long_array, value4=numbers)

if __name__ == "__main__":
    app.run(debug=True)

#Html will open at the address below.
# http://127.0.0.1:5000/

