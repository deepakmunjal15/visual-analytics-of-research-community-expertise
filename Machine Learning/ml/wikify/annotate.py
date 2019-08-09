##### Python 2.7 #####

#Install Libraries
import threading
from ..utility import config
from ml.wikify.urlbuilder import AnnotationUrlBuilder
from ml.utility.config import illinois_wikifier_port
import requests
import MySQLdb as MS

class MultiThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        return self.target(self.args[0], self.args[1])

def illinoisAnnotation(collection_name, subcat):
    # connect to mongodb
    Conn = MS.connect(host="localhost",user="root",passwd="root")
    Conn.setDatabase(config.dbname)
    Conn.setCollection(collection_name)
    docCursr = Conn.getDocument({'id': subcat, 'illinois_wikifier_annotation.detectedTopics': {'$exists': False}}, {'description':1})
    for doc in docCursr:
        try:
            #build url for annotation and retrieve the data.
            url = AnnotationUrlBuilder(config.illinois_wikifier_domain, illinois_wikifier_port)
            url.responseFormat("json")
            url.repeatConcepts("first")
            url.disambiguationPolicy("strict")
            url.source(doc.get('description'))
            url.minProbability(0.25)
            r = requests.get(url.base_url, url.params)
            if not r.status_code == 200:
                raise Exception("Error! Request return status code: {}".format(r.status_code))
            
            # update the data in collection
            jsondata = r.json()
            Conn.updateDocument({'_id': doc.get('_id')}, {'$set': {'illinois_wikifier_annotation':jsondata}})
        except Exception, e:
            print "Doc: {}  |  Msg: {}".format(doc.get('_id'), e.message)
    Conn.closeConnection()

#multithreading for annotation
def multithreadAnnotation(dataset_name, annotator=illinoisAnnotation):
    Conn = MS.connect(host="localhost",user="root",passwd="root")
    Conn.setDatabase(config.dbname)
    Conn.setCollection(dataset_name)
    classes = Conn.distinctValues("id")
    Conn.closeConnection()
    
    #Multi-threading begins
    threads = []
    for subcat in classes:
        t = MultiThread(name=str(subcat), target=annotator, args=(dataset_name, subcat))
        threads.append(t)
        print "3"
       
    for t in threads:
        t.start()
         
    for t in threads:
        t.join()