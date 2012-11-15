import os
from bs4 import BeautifulSoup
import mechanize
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# API goal:
#
# track.config['ct_bbed_5663.scoreFilter'] = 100
# track.config['ct_bbed_5663'] = 'squish'
# track.config.submit()


class ConfigPage(object):
    def __init__(self, url, ucsc_session):
        response = mechanize.urlopen(url)
        self.forms = mechanize.ParseResponse(response, backwards_compat=False)
        self.ucsc_session = ucsc_session
        self.url = url

    def submit(self):
        data = {}
        for form in self.forms:
            text_data = form.click_request_data()[1]
            data.update(dict([i.split('=') for i in text_data.split('&')]))
        logger.debug('data = ' + str(data))
        response = self.ucsc_session.session.get(
            self.url, params=data)
        self.ucsc_session._reset_tracks()
        return response


class TrackException(Exception):
    pass


class Track(object):
    def __init__(self, cell,  ucsc_session):
        """
        `cell` is a <td> tag
        """
        self._cell = cell
        self.ucsc_session = ucsc_session
        a = cell('a')
        select = cell('select')
        if (len(a) != 1) or (len(select) != 1):
            raise TrackException
        select, = select
        a, = a
        try:
            self.visibility = self._cell('option', selected=True)[0].text
            self._visibility_options = [i.text for i in self._cell('option')]
            self.title = a['title']
            self.id = select['name']
            self.label = a.text.strip()
            self.url = os.path.join(ucsc_session.url, a['href'])
        except (KeyError, AttributeError):
            raise TrackException

        self._config = None

    def __repr__(self):
        return '<Track "{id}" ({label}) [{visibility}]>'\
            .format(**self.__dict__)

    @property
    def config(self):
        if self._config is None:
            self._config = self.parse_config()
        return self._config

    def parse_config(self):
        return ConfigPage(self.url, self.ucsc_session)

    def set_visibility(self, visibility):
        if visibility not in self._visibility_options:
            raise ValueError('visibility "%s" not supported by this track; '
                             'options are %s' % self._visibility_options)
        response = self.ucsc_session.track_visibility(self.id, visibility)
        return response


def tracks_from_response(response, ucsc_session):
    soup = BeautifulSoup(response.text)
    cells = soup('td')
    tracks = []
    for cell in cells:
        try:
            track = Track(cell, ucsc_session)
        except TrackException:
            continue
        tracks.append(track)
    return tracks
