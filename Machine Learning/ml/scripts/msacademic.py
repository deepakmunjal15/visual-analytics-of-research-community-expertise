########### Python 2.7 #############

#Install these libraries
import httplib, urllib, base64
import re
import csv
import json
from datetime import date, timedelta
import MySQLdb as MS

#Pass url parameters and Subscription-Key
def interpret(keyword):
    keyword=keyword
    
    headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': 'Create a key',
            }
    
    params = urllib.urlencode({
            # Request parameters
            'query': keyword,
            'complete': '0',
            'count': '1000',
            'offset': '0',
            'timeout': '100',
            'model': 'latest',
            })
    
    try:
        conn = httplib.HTTPSConnection('api.labs.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/interpret?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    values=re.findall(ur'''value":"(.+?)"''', str(data))
    return values

#Extract title, abstract pairs
def title_abstract(values, count_limit, date1, date2):
    title_list=[]
    abstract_list=[]
    headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': 'Create a key',
            }
    k=0
    limit=count_limit
    for i in range(len(values)):
        expr="And("+values[i]+",D=['"+date1+"','"+date2+"'])"
        params = urllib.urlencode({
                # Request parameters
                'expr': expr,
                'attributes': 'E.IA,Ti',
                'count': count_limit,
                'offset': '0',
                'timeout': '100',
                'model': 'latest',
                })
        
        try:
            conn = httplib.HTTPSConnection('api.labs.cognitive.microsoft.com')
            conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            
        data = json.loads(data)
        try:
            for m in range(len(data["entities"])):
                k=k+1
                try:
                    title_list.append([(data["entities"][m]["Ti"]).encode('utf-8')])
                except (KeyError, AttributeError):
                    pass
                    
                #abstract
                try:
                    abstract_list.append([str(data["entities"][m]["IA"]["InvertedIndex"])])
                except (KeyError, AttributeError):
                    abstract_list.append([""])
                
                if abstract_list[-1]==[""] or '' in abstract_list:
                    del title_list[-1]
                    del abstract_list[-1]
                    k=k-1
                
                if (k==limit) or (k>limit):
                    break
            if (k==limit) or (k>limit):
                break
        except (KeyError, AttributeError):
            pass
        
    return title_list, abstract_list

data=[]

#Read all keywords from db
def read_keywords():
    db1 = MS.connect(host="localhost",user="root",passwd="root")
    cursor = db1.cursor()
    cursor.execute("USE mydata;")    
    k=cursor.execute("select * from topics")
    topics_keywords=cursor.fetchall()
    
    # disconnect from server
    db1.close()
    return topics_keywords


final_data=[]

#Extract title and abstract for each keyword
topics_keywords=read_keywords()
for i in range(0, len(topics_keywords)):
    values=interpret(topics_keywords[i][1])
    title_list, abstract_list=title_abstract(values, 1000, str(date.today() - timedelta(days=365*5)), str(date.today()))
    if len(title_list)>0 and len(abstract_list)>0:
        for k in range(len(title_list)):
            title_list[k][0]=title_list[k][0]+"|||"+str(abstract_list[k][0])+"|||"+topics_keywords[i][0]
            final_data.append([title_list[k][0]])

#Save data in a csv file
with open('Path to train_data.csv', 'wb') as fp:
    writer = csv.writer(fp, delimiter ="|", quoting=csv.QUOTE_MINIMAL)
    writer.writerows(final_data)


