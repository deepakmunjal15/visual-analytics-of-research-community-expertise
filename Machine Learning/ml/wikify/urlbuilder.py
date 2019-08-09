from abc import ABCMeta
from ml.utility import convertToASCII

class WikipediaUrlBuilder:
    __metaclass__ = ABCMeta
    def _getBaseUrl(self, domain, port, action):
        self.base_url = "http://{domain}:{port}/illinois-wikifier/services/{action}?"
        if (domain and isinstance(domain, str)) and  (port and isinstance(port, int)) \
                                    and (action and isinstance(action, str)):
            self.base_url = self.base_url.format(domain=domain, port=port, action=action)
        else:
            raise ValueError("Incorrect parameter(s) value(s).")        
    
    def responseFormat(self, response_format):
        if isinstance(response_format, str) and response_format.lower() in ['xml', 'json']:
            self.params["responseFormat"] = response_format.lower()
        else:
            raise ValueError("Incorrect parameter value or type.")

#Sending request to default url: localhost:8080/illinois-wikifier
class IllinoisUrlBuilder(WikipediaUrlBuilder):
    
    def __init__(self, domain, port):
        self._getBaseUrl(domain, port, "wikify")
        self.params = {}
        
    def source(self, text):
        if isinstance(text, unicode):
            text = convertToASCII(text)
            
        if  text and isinstance(text, str):
            self.params['source'] = text
        else:
            raise ValueError("Incorrect value param.")
    
    #To choose if repeat mentions of topics should be tagged or ignored
    def repeatConcepts(self, value):
        if value and isinstance(value, str) and value.lower() in ['all', 'first_in_region', 'first']:
            self.params['repeatMode'] = value.lower()
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    #This specifies the format of the result after wikification.
    def linkFormat(self, value):
        if value and isinstance(value, str) and value.lower() \
                in ['wiki_id_weight', 'auto', 'html_id', 'wiki', \
                    'html_id_weight', 'html', 'wiki_id']:
            self.params['linkFormat'] = value.lower()
    
    #The probability cut-off to decide if a term will be wikified or not. It is left as default of 0.5.
    def minProbability(self, prob):
        if prob and isinstance(prob, float) and prob >= 0.0 and prob <= 1.0:
            self.params['minProbability'] = prob
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    #This is the type of the source document
    def sourceMode(self, mode):
        if mode and isinstance(mode, str) and mode >= 0.0 and mode <= 1.0:
            self.params['sourceMode'] = mode
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    #true if to return a list of topics, otherwise false. Default is true.
    def topics(self, value):
        if value and isinstance(value, bool) :
            self.params['topics'] = value
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    #true to return details of where each topic was found within text, otherwise false
    def topicIndexes(self, value):
        if value and isinstance(value, bool) :
            self.params['references'] = value
        else:
            raise ValueError("Incorrect parameter value or type.")
        
    #wheather each term should be disambiguated to a single interpretation, or to multiple ones
    def disambiguationPolicy(self, value):
        if value and isinstance(value, str) and value.lower() in ['loose', 'strict'] :
            self.params['disambiguationPolicy'] = value.lower()
        else:
            raise ValueError("Incorrect parameter value or type.")