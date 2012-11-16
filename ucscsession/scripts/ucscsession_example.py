import webbrowser
from ucscsession import UCSCSession
import pybedtools

# -----------------------------------------------------------------------------
# Note:  most methods return a requests.Response object
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Begin a session.  A browser window will not pop up until we call the u.show()
# method (this will happen later...)
u = UCSCSession()


# -----------------------------------------------------------------------------
# Upload custom tracks using example data from pybedtools.
for fn in ['a.bed', 'b.bed']:
    x = pybedtools.example_bedtool(fn)\
        .saveas(trackline='track name=%s' % fn)
    response = u.upload_track(x)


# -----------------------------------------------------------------------------
# Set the position of the browser by providing coordinates -- either as
# a string or with an object that has chrom, start, stop attributes.
response = u.set_position('chr1:1-2000')


# -----------------------------------------------------------------------------
# Zoom_in and zoom_out take different levels (1, 2, 3 for 1.5x, 3x, 10x
# respectively), so here we're zooming out 10x
response = u.zoom_out(3)


# -----------------------------------------------------------------------------
# The show() method will open a new tab in your web browser and show a view of
# the current coordinates
response = u.show()

# =============================================================================
# Track configuration
# =============================================================================


# -----------------------------------------------------------------------------
# Tracks are stored as a dictionary of {tracklabel: Track object}.
# So let's inspect our currently-loaded tracks.
from pprint import pprint
pprint(u.tracks)


# -----------------------------------------------------------------------------
# Track visibility can be set in multiple ways.  Say we want to set the custom
# tracks to "pack"; in this case u.set_track_visibilities() is the best choice.
#
# We detect the new tracks by looking for the string "bed" in the track label.
items = []
for k, v in u.tracks.items():
    if 'bed' in v.label:
        items.append((k, 'pack'))
u.set_track_visibilities(items)


# -----------------------------------------------------------------------------
# Let's configure the RefSeq track; for convenience save the Track object as
# `t`
t = u.tracks['refGene']


# -----------------------------------------------------------------------------
# Track.config represents a configuration page for a track.  There can be one
# or more forms on this page, and each form on the configuration page is
# represented as a mechanize.HTMLForm.
#
# It so happens that the refGene track only has a single form.
form = t.config.forms[0]

# -----------------------------------------------------------------------------
# Printing the form tells us the kinds of things it can do.
#
# It's probably good to look at this along with the page itself
print form
webbrowser.open(t.url)

# -----------------------------------------------------------------------------
# Let's enable all possible labels for the refGene track. The names were
# discovered by inspecting the printed form along with the page in the browser
for control in form.controls:
    if control.type == 'checkbox':
        if 'refGene.label' in control.name:
            form[control.name] = ['on']
form['refGene'] = ['pack']

# -----------------------------------------------------------------------------
# After making the configuration changes, submit the changes using the
# ConfigPage object's `submit()` method
response = t.config.submit()


# -----------------------------------------------------------------------------
# Clean up the view a little bit by hiding some tracks
u.set_track_visibilities([
    ('mrna', 'hide'),
    ('intronEst', 'hide'),
    ('knownGene', 'hide'),
])

# -----------------------------------------------------------------------------
# Save a PDF of the new view
u.pdf(filename="example.pdf")
print "pdf saved"

# -----------------------------------------------------------------------------
# And show the final result in the web browser
u.show()
