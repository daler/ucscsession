``ucscsession``
===============
This Python package aims to manage sessions in the UCSC Genome Browser. It
takes inspiration from the R package ``rtracklayer`` but tries to do things in
a more Pythonic manner.

The eventual goal is to integrate this with `pybedtools
<https://github.com/daler/pybedtools>`_ `trackhub
<https://github.com/daler/trackhub>`_, and possibly `cruzdb
<https://github.com/brentp/cruzdb>`_ for full programmatic access to the Genome
Browser for uploading tracks and track hubs, modifying settings, and
downloading PDF screenshots.

This package is still under active development, but currently it can:

* connect to a session on any mirror of the UCSC genome browser
* upload custom tracks
* view current Genome Browser session in a web browser (optionally specifying
  the coordinates of the view)
* download PDFs of screenshots for the current view (or a new set of provided
  coordinates)

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

Copyright 2012 Ryan Dale; BSD 2-clause license.
