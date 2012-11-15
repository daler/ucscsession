"""
useful for debugging ucscsession.tracks.Track
"""
import webbrowser
import ucscsession
import ucscsession.tracks
import pybedtools
from bs4 import BeautifulSoup

reload(ucscsession)
reload(ucscsession.tracks)

u = ucscsession.UCSCSession()
response = u.session.get(u.tracks_url)
b = BeautifulSoup(response.text)

cells = b('td')

# Adjust `start` to skip <td>s with problems
start = 50
for i in range(start, len(cells)):
    try:
        ucscsession.tracks.Track(cells[i], u)
    except ucscsession.tracks.TrackException as e:
        print e.message
