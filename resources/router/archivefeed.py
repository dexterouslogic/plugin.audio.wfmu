import datetime
import urlparse
import xml.etree.ElementTree as ET

import requests

from resources.constants import Const

# helpers

def _ns_tag(tag):
    """Wrap QName attribute value, to allow kenzodb namespace tags to be handled"""
    #http://stackoverflow.com/questions/8113296/supressing-namespace-prefixes-in-elementtree-1-2
    return str( ET.QName(Const.KENZODB_QNAME_URI, tag) )        

# generators
              
def _get_list_items(items):
    def _get_tag(path2):
        return "/".join([_ns_tag('episode'), _ns_tag(path2)])
        # return "{0}/{1}".format(episode_tag, _ns_tag(path2))
    
    for i in items:
        program_title = i.findtext(_ns_tag('programTitle'))

        description = i.findtext( _get_tag('description'))

        ts = i.find(_get_tag('startDate')).attrib.get('unixTimestamp')
        startDate = datetime.datetime.fromtimestamp(int(ts)).strftime('%d.%m.%Y')

        link = i.findtext('link')
        
        result = {
            'label': program_title,
            'info': {
                'date': startDate
            },
            'path': link,
            'is_playable': True,
        }
        
        # if description:
        #     result['label2'] = description

        yield result    

#class
                    
class Router:
    def route(self, show_id=None):
        url = urlparse.urljoin(Const.BASE_URL, "archivefeed/mp3iphone/")

        # if show_id not none and not empty, items are recent show episodes
        # else they are the last x shows broadcast
        if show_id:
            # recent shows for a specific DJ, identified by 2-letter code
            # http://wfmu.org/archivefeed/mp3iphone/KH.xml
            filename = "{0}.xml".format(show_id)
            url = urlparse.urljoin(url, filename)

        # no need to stream small document
        stream = show_id is None

        # get a response, and throw exception if not 200 (requests.codes.ok)
        r = requests.get(url, stream=stream)
        r.raise_for_status()
    
        # parse
        # http://stackoverflow.com/questions/15622027/parsing-xml-file-gets-unicodeencodeerror-elementtree-valueerror-lxml
        if stream:
            r.raw.decode_content = True
            tree = ET.parse(r.raw)
            root = tree.getroot()
        else:
            root = ET.fromstring(r.content)
    
        items = root.findall('channel/item')
        return _get_list_items(items)
    
    