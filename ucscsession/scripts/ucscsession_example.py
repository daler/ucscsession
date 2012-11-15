import webbrowser
from ucscsession import UCSCSession
import pybedtools

# Begin a session.
u = UCSCSession()

# Demonstration of uploading custom tracks; this uses example data from
# pybedtools.
for fn in ['a.bed', 'b.bed']:
    x = pybedtools.example_bedtool(fn)\
        .saveas(trackline='track name=%s' % fn)
    r = u.upload_track(x)


# Set the position of the browser by providing coordinates, either as a string or
u.position('chr1:1-2000')

# zoom_in and zoom_out take different levels (1, 2, 3 for 1.5x, 3x, 10x
# respectively)
r = u.zoom_out(3)

# the show() method will open a new tab in your web browser and show a view of
# the current coordinates
u.show()

# Demo of track configuration.
#
# Track visibility can be set in multiple ways. If all you need is to set
# visibility, then the best way is to do so in bulk, using
# set_track_visibilities().
items = []
for k, v in u.tracks.items():
    if 'bed' in v.label:
        items.append((k, 'pack'))
u.set_track_visibilities(items)

# Alternatively, if you need to set multiple configuration items (as well as
# visibility), then use the track's config page.
#
# Inspect our options for loaded tracks
print u.tracks


# Let's configure the RefSeq track.
t = u.tracks['refGene']

#
# # Each form on the configuration page (there happens to be just one form for
# this particular track) is represented as a mechanize.HTMLForm
form = t.config.forms[0]

# Print the form for a good overview of options and current settings. It's
# probably good to look at this along with the page itself
print form
webbrowser.open(t.url)

# Let's enable all possible labels for the refGene track. The names were
# discovered by inspecting the printed form along with the page in the browser
for control in form.controls:
    if control.type == 'checkbox':
        if 'refGene.label' in control.name:
            form[control.name] = ['on']
form['refGene'] = ['pack']

response = t.config.submit()

u.set_track_visibilities([
    ('mrna', 'hide'),
    ('intronEst', 'hide')
])
u.show()
