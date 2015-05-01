import urlparse
import xml.etree.ElementTree as ET

import requests

from resources.constants import Const

def _get_list_items(shows, plugin):
    """Helper generator for show items"""
    for show in shows:
        # each show must have an id
        id = show.attrib.get('id')
        if not id:
            continue

        # display_title is text of the title element
        e = show.find('title')
        title_text = e.text
        title_sort = e.attrib.get('sort')
        
        dj_names = (djName.text for djName in show.findall('djNames/djName'))
        
        description = show.findtext('description')
    
        yield {
            'label': title_text,
            'label2': description,
            'info': {
                'artist': list(dj_names),
                'title': title_text
            },
            
            'path': plugin.url_for('route_archivefeed', show_id=id),
            'is_playable': False,
        }


class Router:
    def __init__(self, plugin):
        """docstring for __init__"""
        self.plugin = plugin
    
    def route(self):
        # http://wfmu.org/recent_archive_programs.php?xml=1
        url = urlparse.urljoin(Const.BASE_URL, "recent_archive_programs.php")
        payload = {
            'xml': 1
        }
        
        r = requests.get(url, params=payload, stream=True)
        r.raw.decode_content = True
        r.raise_for_status()

        tree = ET.parse(r.raw)
        root = tree.getroot()
 
        shows = root.findall('show')

        return _get_list_items(shows, self.plugin)