``ucscsession``
===============
This Python package aims to manage sessions in the UCSC Genome Browser. It
takes inspiration from the R package ``rtracklayer`` but tries to do things in
a more Pythonic manner.

The eventual goal is to integrate this with `pybedtools
<https://github.com/daler/pybedtools>`_, `trackhub
<https://github.com/daler/trackhub>`_, and possibly `cruzdb
<https://github.com/brentp/cruzdb>`_ for full programmatic access to the Genome
Browser for uploading tracks and track hubs, modifying settings, and
downloading PDF screenshots.

This package is still under active development, but currently it can:

* Connect to a session on any mirror of the UCSC genome browser
* Upload custom tracks
* View current Genome Browser session in a web browser (optionally specifying
  the coordinates of the view)
* Download PDFs of screenshots for the current view (or a new set of provided
  coordinates)
* Inspect currently loaded tracks
* Make bulk track visibility changes or change visibility one-by-one
* Zoom in and out from the current coordinates
* Log in to an account and use tracks loaded in that session
* Change any setting on any track, thanks to the `mechanize
  <http://wwwsearch.sourceforge.net/mechanize/>`_


Example usage::

    import ucscsession
    import pybedtools

    # Initialize a session
    u = ucscsession.UCSCSession()

    # Upload some example BED files
    for fn in ['a.bed', 'b.bed']:
        x = pybedtools.example_bedtool(fn)\
            .saveas(trackline='track name=%s' % fn)
        r = u.upload_track(x)

    # Save a PDF at a particular position
    print "PDF file at %s" % u.pdf(position='chr1:1-2000')

    # Display in a web browser
    u.show()

    # set the visibility of all tracks with "bed" in the label to "squish"
    tracks = []
    visibilities = []
    for k, v in u.tracks.items():
        if 'bed' in v.label:
            tracks.append(k)
            visibilities.append('squish')
    u.set_track_visibilities(tracks, visibilities)

    # Zoom out a little
    u.zoom_out()

    # Show the new view in a new browser tab -- zoomed out, and with the custom
    # tracks set to "pack" visibility
    u.show()


Copyright 2012 Ryan Dale; BSD 2-clause license.

.. include:: ucscsession/blob/master/LICENSE

