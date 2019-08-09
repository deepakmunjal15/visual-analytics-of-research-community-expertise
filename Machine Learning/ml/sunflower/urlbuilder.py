
from abc import ABCMeta

class SunflowerUrlBuilder:
    __metaclass__ = ABCMeta
    def _getBaseUrl(self, domain, port):
        self.params = {}
        self.base_url = "http://{domain}:{port}/sunflower/concept"
        if (domain and isinstance(domain, str)) and  (port and isinstance(port, int)):
            self.base_url = self.base_url.format(domain=domain, port=port)
        else:
            raise ValueError("Incorrect parameter(s) value(s).")        
    
    def responseFormat(self, response_format):
        if isinstance(response_format, str) and response_format.lower() in ['xml', 'json']:
            self.params["responseFormat"] = response_format.lower()
        else:
            raise ValueError("Incorrect parameter value or type.")

    def width(self, v=5):
        if isinstance(v, int) and v <= 5 and v >= 1:
            self.params['width'] = v
        else:
            raise ValueError("Incorrect parameter value or type.")
        
    def depth(self, v=5):
        if isinstance(v, int) and v <= 5 and v >= 1:
            self.params['depth'] = v
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    def noPrunning(self, v=False):
        if isinstance(v, bool):
            self.params['noPruning'] = str(v).lower()
        else:
            raise ValueError("Incorrect parameter value or type.")
    
    def fullLabels(self, v=True):
        if isinstance(v, bool):
            self.params['fullLabels'] = str(v).lower()
        else:
            raise ValueError("Incorrect parameter value or type.")

#This class is used to build url to get concept's graph from sunflower implementation.
class ConceptGraphUrlBuilder(SunflowerUrlBuilder):
    def __init__(self, domain, port, concept):
        self._getBaseUrl(domain, port)
        if isinstance(concept, str):
            concept_vals = concept.strip().lower().split(' ')
            formatted_concept = '_'.join(concept_vals)
            self.base_url += "/{action}/{query}".format(action='graph', query=formatted_concept)

#This class is used to build url to get concept's paths from sunflower implementation.
class ConceptPathsUrlBuilder(SunflowerUrlBuilder):
    def __init__(self, domain, port, concept):
        self._getBaseUrl(domain, port)
        if isinstance(concept, str):
            concept_vals = concept.strip().lower().split(' ')
            formatted_concept = '_'.join(concept_vals)
            self.base_url += "/{action}/{query}".format(action='paths', query=formatted_concept)   
            
    
