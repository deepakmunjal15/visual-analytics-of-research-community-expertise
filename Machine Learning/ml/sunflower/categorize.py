
import MySQLdb as MS
from pubexpert.utility import config, convertToASCII
from pubexpert.sunflower.urlbuilder import ConceptPathsUrlBuilder
import requests
from pubexpert.wikify.annotate import multiProcessAnnotation
import time

width = 4
depth = 4

# building url for annotation and retrieving the data.
def wikiCategoriesForAConcept(concept):
    try:
        url = ConceptPathsUrlBuilder(domain=config.sunflower_domain, port=config.sunflower_port, concept=concept)
        url.responseFormat("json")
        url.depth(v=depth)
        url.width(v=width)
        url.fullLabels()
        url.noPrunning()
        time.sleep(0.2)
        r = requests.get(url.base_url, url.params)
        if not r.status_code == 200:
            raise Exception("Error! Request return status code: {}".format(r.status_code))
        
        #update the data in collection
        jsondata = r.json()
        categories = set()
        
        for response_category in jsondata:
            #get category from 'concept' key
            categories.add(response_category.get('concept').split(':')[1])
            # get categores from 'edges' key
            for edge in response_category.get('edges'):
                categories.add(edge.get('name').split(':')[1])
        return list(categories), {'width':url.params.get('width'), 'depth': url.params.get('depth')}
    
    except Exception as e:
        print "Concept: {}  |  Msg: {}".format(concept, e.message)
        return [], {}

def categorizeConcepts(collection_name, subcat):
    # connect to db
    Conn = MS.connect(host="localhost",user="root",passwd="root")
    Conn.setDatabase(config.dbname)
    Conn.setCollection(collection_name)
    docCursr = Conn.getDocument({'nserc_cat_id': subcat, 'illinois_wikifier_annotation.category_request.width':{'$exists':False}}, {'illinois_wikifier_annotation.detectedTopics':1})
    for doc in docCursr:
        try:
            wiki_concepts = doc.get('illinois_wikifier_annotation').get('detectedTopics', [])
            category_request = {}
            for topic_dict in wiki_concepts:
                title = topic_dict.get('title', '')
                formatted_title = convertToASCII(title).strip().lower().split(' ')
                formatted_title = '_'.join(formatted_title)
                categories = wikiCategoriesForAConcept(formatted_title)
                topic_dict[unicode('categories')] = categories[0]
                category_request = categories[1]
            Conn.updateDocument({'_id': doc.get('_id')},
                                     {'$set': {'illinois_wikifier_annotation.detectedTopics':wiki_concepts,
                                               'illinois_wikifier_annotation.category_request': category_request
                                               }
                                    })
        except Exception as e:
            print "_id: {}  |  Msg: {}".format(doc.get('_id'), e.message)
    
    Conn.closeConnection()

def multiprocessConceptCategories(dataset_name, w, d):
    width = w
    depth = d
    multiProcessAnnotation(dataset_name, target=categorizeConcepts)
