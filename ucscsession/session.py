import pybedtools
import webbrowser
import requests
import os
from bs4 import BeautifulSoup
import helpers
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_ucsc_session_instance = [None]

import settings


def change_mirror(mirror):
    settings.mirror = mirror


def UCSCSession():
    """
    Create and interact with a session in the UCSC Genome Browser.

    Use change_mirror() to change the mirror that will be used; by default
    it's http://genome.ucsc.edu.
    """
    if not _ucsc_session_instance[0]:
        _ucsc_session_instance[0] = _UCSCSession()
    return _ucsc_session_instance[0]


class _UCSCSession(object):
    def __init__(self):
        self._session = None
        self._mirror = settings.mirror
        self.cart = self.cart_info()

    def update_cart(self, **kwargs):
        """
        Update the current settings.

        For example. change the assembly with

        update_cart(db="dm3")

        """
        self.session.get(self.cart_url, data=kwargs)

    @property
    def session(self):
        """
        Creates a new session if none exists, or if the mirror has changed.
        """
        if (settings.mirror != self._mirror) or (self._session is None):
            logger.debug('init session')
            self._mirror = settings.mirror
            self._session = requests.session(params=dict(hgsid=self.hgsid))
        return self._session

    @property
    def hgsid(self):
        """
        Get a new hgsid if one has not been set or if the mirror has changed;
        otherwise return the existing one.
        """
        if (settings.hgsid is None) or (self._mirror != settings.mirror):
            logger.debug('new hgsid: %s' % settings.hgsid)
            settings.hgsid = helpers.hgsid_from_response(
                requests.get(self.gateway_url))
        logger.debug('hgsid=%s' % settings.hgsid)
        return settings.hgsid

    # -------------------------------------------------------------------------
    # Here are a bunch of getter methods that provide up-to-date URLs depending
    # on the current state of settings.mirror.
    @property
    def url(self):
        return os.path.join(settings.mirror, 'cgi-bin')

    @property
    def gateway_url(self):
        return os.path.join(self.url, 'hgGateway')

    @property
    def tracks_url(self):
        return os.path.join(self.url, 'hgTracks')

    @property
    def custom_url(self):
        return os.path.join(self.url, 'hgCustom')

    @property
    def tables_url(self):
        return os.path.join(self.url, 'hgTables')

    @property
    def cart_url(self):
        return os.path.join(self.url, 'cartDump')

    @property
    def hub_url(self):
        return os.path.join(self.url, 'hgHubConnect')

    # -------------------------------------------------------------------------

    def cart_info(self):
        """
        Return a dictionary of the current cart

        (which has all the CGI vars in it)
        """
        logger.debug('accessing cart')
        r = self.session.get(self.cart_url)
        b = BeautifulSoup(r.text)
        d = dict([i.split(None, 1) for i in b.pre.text.splitlines(False)])
        return d

    def upload_track(self, track, trackline=None):
        """
        Uploads a track, providing an optional track line.

        The track line will automatically have a newline added if none exists.
        """
        if isinstance(track, pybedtools.BedTool):
            if trackline:
                track = track.saveas(trackline=trackline)
                track = track.fn
        else:
            if trackline:
                fout = open(pybedtools.BedTool._tmp(), 'w')
                fout.write(trackline.rstrip() + '\n')
                fout.write(open(track))
                fout.close()
                track = fout.name

        return self.session.post(
            self.custom_url,
            files={'hgt.customFile': open(track)}
        )

    def show(self, position=None):
        """
        Open a browser window at `position`.

        `position` should be either an object with chrom, start, stop
        attributes (like a pybedtools.Interval) or a string of the form
        "chrom:start-stop".

        If `position` is None, then just use the last position.
        """
        payload = {}
        payload.update({'position': self._position_string(position)})
        response = self.session.get(self.tracks_url, data=payload)
        webbrowser.open(response.url)
        return response

    def pdf(self, position=None, filename=None):
        """
        Save a PDF of the current browser view.

        If `position` is None, then use the last available position.

        If `filename` is None, then a temporary file will be created.

        Returns the created filename.
        """
        payload = {'hgt.psOutput': 'on'}
        payload.update(position=self._position_string(position))
        response = self.session.post(self.tracks_url, data=payload)
        link = helpers.pdf_link(response)
        logger.debug('PDF link: %s' % link)
        if filename is None:
            filename = pybedtools.BedTool._tmp()
        pdf_content = self.session.get(link)
        fout = open(filename, 'w')
        fout.write(pdf_content.content)
        fout.close()
        return filename

    def _position_string(self, position):
        """
        Given either a string or an object with chrom/start/stop, always return
        a position string in the form "chrom:start-stop"
        """
        if not position:
            position = self.cart_info()['position']
        if not isinstance(position, basestring):
            position = '{chrom}:{start}-{stop}'.format(position)
        return position


u = UCSCSession()
for fn in ['a.bed', 'b.bed']:
    x = pybedtools.example_bedtool(fn)\
        .saveas(trackline='track name=%s' % fn)
    r = u.upload_track(x)

print "PDF file at %s" % u.pdf(position='chr19:1-5000')
