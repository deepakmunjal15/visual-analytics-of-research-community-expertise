################## Python 2.7 ######################
# encoding: utf-8
#Install libraries
from optparse import OptionParser
import sys
from sklearn.svm.classes import LinearSVC
from ml.utility import readCSVToDF, config
from ml.classifier_helper import getFeatures, createTrainTFIDF, createTestTFIDFTransformation, \
    __getVectorizer, classify
from sklearn.cross_validation import StratifiedShuffleSplit
import warnings
import bson
import re
import MySQLdb as MS
import pandas as pd
import ast

# parse commandline arguments
op = OptionParser()
op.add_option("--exclude_classes", action="store", type="str", dest="remove_classes",
              help="Name the classes by comma separated values. This option removes listed classes from \
              the train and test")
op.add_option("--model_type", action='store', type='str', dest='model_type',
              help='Type of classification task takes one of the values, bow,boc,bok.')
op.add_option('--store_classifiers', action='store_true', dest='store_classifiers',
              help='Stores the classifiers. Generates warning and user prompt if already exists for an \
              overwrite.')
op.add_option('--use_available_classifiers', action='store_true', dest='available_classifiers',
              help='Uses previously generated classifiers. If does not exists, new classifier models are \
              generated.')
op.add_option("--random_state", action='store', type='int', dest='random_state',
              help='Use random value of type int to reproduce the results.')
(opts, args) = op.parse_args()

if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)
if __doc__:
    print(__doc__)
op.print_help()

clfs = (
            (LinearSVC(), "Linear SVC"),
        )

# total results from classifier
def calculateScore(result, n_folds):
    print 'x' * 70
    n_classifier = len(clfs)
    for x in xrange(n_classifier):
        a=0.0
        p=0.0
        r=0.0
        f1=0.0
        for i in xrange(x * n_folds, (x * n_folds) + n_folds):
            a += result[i][0]
            p += result[i][1]
            r += result[i][2]
            f1 += result[i][3]
        a, p, r, f1 = a / n_folds, p / n_folds, r / n_folds, f1 / n_folds
        print "Classifier: {}".format(clfs[x][1])
        print('Accuracy:%0.2f' % (a))
        print('Precision:%0.2f' % (p))
        print('Recall:%0.2f' % (r))
        print('F1-Score:%0.2f' % (f1))  
        print '_' * 30
        
#Create TFIDF
def vectorize(data_train, data_test, vocabulary=None, binary=False):
    if opts.verbose > 0:
        print "Creating TFIDF matrix for training and test dataset."
    vectorizer = __getVectorizer(max_df=1.00, min_df=1, vocabulary=vocabulary, binary=binary)
    X_train = createTrainTFIDF(data_train, vectorizer)
    X_test = createTestTFIDFTransformation(data_test, vectorizer)
    return X_train, X_test , vectorizer     

#Running Classifier on the data
def runClassification(clf, X_train, X_test, target_train, target_test, cv=0):
    if opts.verbose > 0:
        print "Classification begins."
      
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return_tuple = classify(clf, X_train, X_test, target_train, target_test, opts.verbose, cv, average='macro')
        if len(return_tuple) == 1:
            test_idx = return_tuple[0]
        if len(return_tuple) == 5:
            accuracy, precision, recall, f1, test_idx = return_tuple
        probabilities = []
        for rlist in test_idx:
            probabilities.append(rlist[3].tolist())
        if len(return_tuple) == 1:
            return [probabilities]
        return [accuracy, precision, recall, f1, probabilities ]


#Converting Microsoft Academic extracted Abstract into human-readable textual form
def convert_to_abstract(mydict):
    mydict=ast.literal_eval(mydict)
    all_indexes=[]
    for key in mydict:
        value=mydict[key]
        for i in range(len(value)):
            all_indexes.append(int(value[i]))

    max_index=max(all_indexes)
    abstract_list=["" for i in range(max_index+1)]
    
    for key in mydict:
        value=mydict[key]
        for i in range(len(value)):
            abstract_list[value[i]]=key

    temp=""
    for i in range(len(abstract_list)):
        if i==0:
            temp=temp+abstract_list[i]
        else:
            temp=temp+" "+abstract_list[i]
        
    abstract=temp
    return abstract

#Get indexes from cv and creates array of data for corresponding indices and returns tuple of temp_train_data, temp_test_data, temp_train_target, temp_test_target,temp_train_ids, temp_test_ids
def getCVData(d, cv):
    
    #Access training data
    df = pd.read_csv("Path to train_data.csv")
    df=df.as_matrix()
    title_abstract=[]
    for i in range(len(df)):
        temp=unicode(df[i][0], 'utf-8')+" "+convert_to_abstract(df[i][1])
        title_abstract.append(temp)
    
    temp_train_data, temp_test_data, temp_train_target, temp_test_target = [], [], [], []
    temp_train_ids, temp_test_ids = [], []
    
    for train_index, test_index in cv:   
        for i in train_index:
            temp_train_data.append(d.get('data')[i])
            temp_train_target.append(d.get('target')[i])
            temp_train_ids.append(d.get('Ids')[i])
        for i in test_index:    
            temp_test_data.append(d.get('data')[i])
            temp_test_target.append(d.get('target')[i])
            temp_test_ids.append(d.get('Ids')[i]) 
    return temp_train_data, temp_test_data, temp_train_target, temp_test_target, temp_train_ids, temp_test_ids       

#Connecting to db and storing all results
def storeResult(probabilities, class_order, level, task, test_Ids, test_targets, collname):
    conn = MS.connect(host="localhost",user="root",passwd="root")
    conn.setDatabase(config.dbname)
    conn.setCollection(collname)
    skip_labels = False
    if len(test_targets) == 0:
        test_targets = test_Ids
        skip_labels = True
        
    for p, did, label in zip(probabilities, test_Ids, test_targets):
        patt = re.compile('[a-f0-9]{24}')
        matches = patt.findall(did)
        did = matches[0]
        did = bson.ObjectId(did)
        doc = [d for d in conn.getDocument({'_id':did})]
        if len(doc) == 1 :
            result = {}
            result['class_probabilities'] = dict(zip(class_order, p))
            task_subdoc = None
            if isinstance(doc[0].get(task), list):
                task_subdoc = doc[0].get(task)
                task_subdoc.append(result)
            else:
                task_subdoc = [result] 
            conn.updateDocument({'_id':did}, {'$set':{task:task_subdoc}})
                
        else:
            d, result = {}, {}
            result['class_probabilities'] = dict(zip(class_order, p))
            if not skip_labels:
                d['label'] = label
            d['_id'] = did
            d[task] = [result]
            conn.insertDocument(d)
    conn.closeConnection()

#Dividing data into 70-30% for training and testing respectively
def train_test_split(list_of_df, test_ratio=0.3):
    test_data = []
    test_target = []
    test_Ids = []
    for d in list_of_df: 
        train_test_stratified_shuffle_split = StratifiedShuffleSplit(d.get('target'), 1, \
                                              test_size=test_ratio, random_state=opts.random_state)
        temp_train_data, temp_test_data, temp_train_target, temp_test_target, temp_train_ids, temp_test_ids = \
            getCVData(d, train_test_stratified_shuffle_split)        
        d['data'], d['target'] = temp_train_data, temp_train_target
        d['Ids'] = temp_train_ids
        test_data.extend(temp_test_data)
        test_target.extend(temp_test_target)
        test_Ids.extend(temp_test_ids)
    
    return test_data, test_target, test_Ids 

#Get data from the database
def getTestDataFromDb(collection_name, model_type):
    conn = MS.connect(host="localhost",user="root",passwd="root")
    conn.setDatabase(config.dbname)
    conn.setCollection(collection_name)
    docCursor = conn.getDocument({})
    test_data, test_target, test_Ids = [], [], []
    for doc in docCursor:
        if model_type == 'bow':
            test_data.append(doc.get('bow_v2'))
        if model_type == 'boc':
            test_data.append(doc.get('categories'))
        if model_type == 'bok':
            test_data.append(doc.get('concepts'))
        test_Ids.append(str(doc.get('_id')))
    conn.closeConnection()
    return test_data, test_target, test_Ids

if __name__ == '__main__':
    try:
        opts.filenames = [v.strip() for v in opts.filenames.split(',')]
        if opts.class_labels:
            opts.class_labels = [v.strip() for v in opts.class_labels.split(',')]
        if not opts.random_state:
            opts.random_state = 33
    except Exception as e:
        print "Error! {}".format(e.message)
        sys.exit(1)

#Load dataset and create data and targets
    for model_type in opts.model_type.split(','):
        list_of_df = []
        for filename, label in zip(opts.filenames, opts.class_labels):
            d = {}
            df = readCSVToDF(filename, header_names=['Id', 'Text'])
            select_column = None
            if model_type == 'bow':
                select_column = 'Text'
            elif model_type == 'boc':
                select_column = 'Concepts'
            elif model_type == 'bok':
                select_column = 'Categories'
            d['data'] = [s[0] for s in df.as_matrix([select_column]).tolist()]
            d['target'] = [s[0] for s in df.as_matrix(['Text']).tolist()]
            d['Ids'] = [s[0] for s in df.as_matrix(['Id']).tolist()]
            d['label'], d['filename'] = label, filename
            
        if opts.cv > 1:
            pass
        else:
            test_data, test_target, test_Ids, test_target_parent_label = train_test_split(list_of_df, test_ratio=0.3)
            results = []
#Creating  binary tfidf vectors for BOC and BOK
            if model_type in ['boc', 'bok']:
                X_train, X_test, vectorizer = vectorize(test_data, binary=True)
            else:
                X_train, X_test, vectorizer = vectorize(test_data)
            feature_names = getFeatures(vectorizer)
            clf = LinearSVC()
            result = runClassification(clf, X_train, X_test)
            storeResult(result[-1], clf.classes_, 0, model_type , test_Ids, test_target)    
            calculateScore([result[:-1]], 1)