import urlparse
import xml.etree.ElementTree as ET

import requests

from resources.constants import Const
# from resources.lib import requests


class Router:
    def __init__(self, addon):
        self.addon_id = addon.getAddonInfo('id')

    def _get_list_items(self, channels, bitrate=None, default_channel_id=None):
        """Get iterator for live streams (channels)"""
        def _get_streams(channel, fmt='mp3'):
            """Get a stream from a channel element"""
            # attribute expression not supported in python 2.6,
            # so this won't work
            # xpath = "streams/stream[@format='{0}']".format(format)
            # if bitrate:
            #     xpath += "[bitrate='{:d}']".format(bitrate)
            for stream in channel.findall("streams/stream"):
                if fmt and stream.attrib.get('format') != fmt:
                    continue

                if bitrate and int(stream.findtext("bitrate")) != bitrate:
                    continue

                yield stream

        # special://home/addons/.../resources/
        thumbnails_base_url = Const.RESOURCES_URL_FORMAT.format(self.addon_id) + "media/thumbnails/"

        for c in channels:
            # any context will do
            title = c.find("titles/title").text
            id = int(c.attrib.get('id'))

            # find the stream with the default bitrate
            # streams = findall_streams(channel, bitrate=bitrate)
            # if not streams:
            streams = _get_streams(c)

            # yield all streams (not just highest rate)
            for stream in streams:
                # thumbnails are stored in resources/media/thumbnails/$ID.png
                path = stream.findtext('directUrl')
                thumbnail = "{0}{1:d}.png".format(thumbnails_base_url, id)
                br = int(stream.findtext("bitrate"))

                yield {
                    'label': "{0} [{1}Kb/s]".format(title, br),
                    'path': path,
                    'thumbnail': thumbnail,
                    'is_playable': True,
                    'stream_info': {
                        'codec': stream.attrib.get('format')
                    }
                    # 'selected': id == default_channel_id,
                    # 'icon': stream.findtext('iconUrl'),
                    # 'info': {
                    #     'count': int(stream.findtext('bitrate'))
                    # },
                }

            # choose highest rate stream by default
            # try:
            #     stream = max(streams, key=lambda s: int(s.findtext('bitrate')))
            # except ValueError:
            #     # requires >= 1 streams
            #     continue
            # else:
            #     # thumbnails are stored in resources/media/thumbnails/$ID.png
            #     path = stream.findtext('directUrl')
            #     thumbnail = "{0}{1:d}.png".format(thumbnails_base_url, id)

            #     yield {
            #         'label': title,
            #         'path': path,
            #         'thumbnail': thumbnail,
            #         # 'selected': id == default_channel_id,
            #         'is_playable': True,
            #         #'icon': stream.findtext('iconUrl'),
            #         # 'info': {
            #         #     'count': int(stream.findtext('bitrate'))
            #         # },
            #         'stream_info': {
            #             'codec': stream.attrib.get('format')
            #         }
            #     }

    def route(self):
        """Get a iter of items representing each channel's live stream
        see: http://wfmu.org/channels_feed.php?xml=1
        """
        url = urlparse.urljoin(Const.BASE_URL, "channels_feed.php")
        payload = {
            'xml': 1
        }

        r = requests.get(url, params=payload, stream=False)
        r.raise_for_status()

        root = ET.fromstring(r.content)

        # every channel contains multiple streams
        channels = root.findall('channel')
        # use default channel to make default selection
        default_channel_id = int(root.find('defaultChannel').attrib.get('id'))

        return self._get_list_items(channels, default_channel_id=default_channel_id)
