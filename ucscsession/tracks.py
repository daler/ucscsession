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

    def print_forms(self):
        for i, form in enumerate(self.forms):
            print "forms[{0}]".format(i)
            for control in form.controls:
                try:
                    if control.type in ['hidden', 'submit']:
                        continue
                except (KeyError, AttributeError):
                    pass
                print '   {0}'.format(control)


class TrackException(Exception):
    pass


class Track(object):
    def __init__(self, td,  ucsc_session):
        """
        `td` is a <td> tag parsed with BeautifulSoup
        """
        self._td = td
        self.ucsc_session = ucsc_session

        # Filter out <td> cells containing known sentinel text indicating it
        # doesn't represent a track
        td_str = str(td)
        if 'toggleButton' in td_str:
            raise TrackException(
                '<td> contains a group toggle button:\n %s' % td_str)
        if len(td('b')) > 0:
            raise TrackException(
                '<td> looks like a group title:\n %s' % td_str)
        if 'hgt.refresh' in td_str:
            raise TrackException(
                '<td> looks like a refresh button:\n %s' % td_str)
        if '[No data' in td_str:
            raise TrackException(
                '<td> is reporting no data for this chrom:\n %s' % td_str)

        # Extract the config page URL for this track.
        #
        # Note: for liftedOver or ENCODE tracks, there's another <a> tag for
        # the little icon thing, which will be the first <a> tag in the table
        # cell.  Otherwise, there should be just one <a> tag.
        a = td('a')
        if (len(a) == 0):
            raise TrackException('<td> has no <a> tag:\n %s' % td_str)
        a = a[-1]
        self.url = os.path.join(ucsc_session.url, a['href'])

        # Extract the <select> and current visibility
        select = td('select')
        if len(select) != 1:
            raise TrackException('<td> has no <select> tag:\n %s' % td_str)
        select = select[0]
        self.visibility = self._td('option', selected=True)[0].text
        self._visibility_options = [i.text for i in self._td('option')]

        # Extract out some other stuff useful for introspection
        self.id = select['name']
        self.label = a.text.strip()

        # Sometimes there's no title; in that case set it to the label.
        try:
            self.title = a['title']
        except KeyError:
            self.title = self.label
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
