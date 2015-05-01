from xbmcswift2 import Plugin, SortMethod

from resources.constants import Const
from resources.router import channels, archivefeed, recent

plugin = Plugin()
@plugin.route('/')
def index():
    return [
        {'label': plugin.get_string(30001), 'path': plugin.url_for('route_channels')},
        {'label': plugin.get_string(30002), 'path': plugin.url_for('route_archive')},
    ]
    
#

@plugin.route('/archive/')
def route_archive():
    return [
        {'label': plugin.get_string(30003), 'path': plugin.url_for('route_archivefeed_all')},
        {'label': plugin.get_string(30004), 'path': plugin.url_for('route_recent_archive_programs')},
    ]
    
# @plugin.route('/channels/')
@plugin.cached_route('/channels/')
def route_channels():
    return list(channels.Router(plugin.addon).route())

#
    
@plugin.cached(TTL=Const.ARCHIVE_CACHE_TTL)
def _route_archivefeed(show_id):
    """cacheable route_archivefeed()"""
    router = archivefeed.Router()
    return list(router.route(show_id))

@plugin.route('/archive/feed/', name='route_archivefeed_all')
@plugin.route('/archive/feed/<show_id>/')
def route_archivefeed(show_id=None):
    # archivefeed is what normal people would call 'last few days'
    items = _route_archivefeed(show_id)
        
    return plugin.finish(items, sort_methods=[
        SortMethod.DATE,
        SortMethod.TITLE, 
        SortMethod.ARTIST,
    ])
  
# 

@plugin.cached(TTL=Const.ARCHIVE_CACHE_TTL)
def _route_recent_archive_programs():
    router = recent.Router(plugin)
    return list(router.route())
    
@plugin.route('/archive/recent/')
def route_recent_archive_programs():
    # recent is what normal people would call 'all'
    items = _route_recent_archive_programs()
    
    return plugin.finish(items, sort_methods=[
        SortMethod.TITLE, 
        SortMethod.ARTIST
    ])

# main

if __name__ == '__main__':
    plugin.run()
