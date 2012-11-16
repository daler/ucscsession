.. _quickstart:

Quickstart
==========
Viewing in a web browser
------------------------

Start by importing the module and creating a :class:`UCSCSession`.

.. doctest::

    >>> from ucscsession import UCSCSession
    >>> u = UCSCSession()
    >>> u.set_genome('hg19')
    <Response [200]>

.. doctest::
    :hide:

    >>> from ucscsession import settings
    >>> settings.hgsid = 311279751

We can immediately view it in a web browser and it will show just the default
tracks:

.. doctest::

    >>> response = u.show()

.. note::

    By default, calling ``u.show`` imposes a 2-second delay after opening the
    web browser.

    This seems to make the web browser view reflect the state of the genome
    browser at the time ``u.show`` was called.  Otherwise, by the time the
    image is created by the server, sent to your computer, and displayed in
    your web browser, subsequent Python code may have already changed the state
    of the genome browser -- sometimes resulting in confusing results.

    You can change this behavior by adjusting the :attr:`UCSCSession._SLEEP`
    class variable.

Uploading custom tracks
-----------------------

To demonstrate custom track uploads, let's upload some example data that comes
with :mod:`pybedtools`.  :meth:`UCSCSession.upload_track` will accept either
a :class:`pybedtools.BedTool` object or a filename:

.. doctest::

    >>> import pybedtools

    >>> # Upload using the BedTool object
    >>> a =  pybedtools.example_bedtool('a.bed')\
    ...     .saveas(trackline='track name="custom, a.bed"')
    >>> response = u.upload_track(a)

    >>> # Upload using a filename
    >>> b = pybedtools.example_bedtool('b.bed')\
    ...     .saveas(trackline='track name="custom, b.bed"')
    >>> response = u.upload_track(b.fn)

Now when we view the session again, the tracks should be visible.  To make sure
we can see the data from the custom tracks, we can provide coords as a string.
It's also possible to pass an interval-like object (with chrom, start, and stop
attributes) instead of a string.

.. doctest::

    >>> u.show('chr1:1-2000')
    <Response [200]>


There's not really anything interesting in this part of the genome, so let's
zoom out 10x.  Levels of 1, 2, and 3 correspond to 1.5x, 3x, and 10x just like
the buttons in top right of the browser. When :meth:`UCSCSession.show` is
called without a position, it uses the currently set position.

.. doctest::

    >>> u.zoom_out(3)
    <Response [200]>

    >>> u.show()
    <Response [200]>

Saving PDFs
-----------
Let's take a PDF snapshot.  Just like :meth:`UCSCSession.show`, if no `position` is
provided then it will use the current position:

.. doctest::

    >>> u.pdf(filename='example.pdf')
    'example.pdf'

Like the ``show`` method, the ``pdf`` method also imposes a default 2-second
delay.  You can open up :file:`example.pdf` to confirm that the PDF was saved.


Track introspection
-------------------
:attr:`UCSCSession.tracks` is a dictionary of the currently-loaded tracks.  The
keys are track labels (set by UCSC), and the values are
:class:`ucscsession.tracks.Track` objects.

Let's see what our options are; here are the first 25 tracks.  Note that custom
tracks start with the ``ct`` prefix:

.. doctest::

    >>> for k in sorted(u.tracks.keys())[:25]:
    ...    print k
    HInvGeneMrna
    acembly
    affyExonArray
    affyGnf1h
    affyU133
    affyU133Plus2
    affyU95
    allHg19RS_BW
    allenBrainAli
    altSeqComposite9
    bacEndPairs
    burgeRnaSeqGemMapperAlign
    ccdsGene
    cgapSage
    chainSelf
    cons46way
    consIndelsHgMmCanFam
    cosmic
    cpgIslandExt
    ct_customabed_9933
    ct_custombbed_6497
    ctgPos
    ctgPos2
    cutters
    cytoBand

How many tracks are available?

.. doctest::

    >>> print len(u.tracks)
    151


Every one of these tracks can be configured via :mod:`ucscsession`.  Some have
very basic config options (e.g., only the ability to set visibility) while
others can be quite complex (e.g., the ENCODE tracks).

Printing a single track indicates its current visibility:

.. doctest::

    >>> print u.tracks['refGene']
    <Track "refGene" (RefSeq Genes) [dense]>

Let's get a small list, showing only the visible tracks:

.. doctest::

    >>> for k in sorted(u.tracks.keys()):
    ...     track = u.tracks[k]
    ...     if track.visibility == 'hide':
    ...         continue
    ...     print '%s: %s' % (k, u.tracks[k])
    cons46way: <Track "cons46way" (Conservation) [full]>
    ct_customabed_9933: <Track "ct_customabed_9933" (custom, a.bed) [dense]>
    ct_custombbed_6497: <Track "ct_custombbed_6497" (custom, b.bed) [dense]>
    intronEst: <Track "intronEst" (Spliced ESTs) [dense]>
    knownGene: <Track "knownGene" (UCSC Genes) [pack]>
    mrna: <Track "mrna" (Human mRNAs) [dense]>
    refGene: <Track "refGene" (RefSeq Genes) [dense]>
    rmsk: <Track "rmsk" (RepeatMasker) [dense]>
    ruler: <Track "ruler" (Base Position) [dense]>
    snp135Common: <Track "snp135Common" (Common SNPs(135)) [dense]>
    wgEncodeReg: <Track "wgEncodeReg" (ENCODE Regulation...) [show]>

Track visibility
----------------
It's possible to adjust the visibility of each track by going to its
configuration page and adjusting the visibility, but that requires a request
for each config page.  Instead, it's more efficient to provide a list of
(trackname, visibility) tuples to :meth:`UCSCSession.set_track_visibilities`.

Here we hide everything except the custom tracks and refGene track:

.. doctest::

    >>> items = []
    >>> for t in u.tracks.values():
    ...    if t.id.startswith('ct') or t.id == 'refGene':
    ...        continue
    ...    if t.visibility == 'hide':
    ...        continue
    ...    items.append((t.id, 'hide'))
    >>> u.set_track_visibilities(items)
    <Response [200]>


.. doctest::

    >>> u.show()
    <Response [200]>


Configuring tracks
------------------
As a reasonable example, let's work on the ``refGene`` track.  This track has
settings like which labels to show, standard visibility settings, and some
codon display settings.

First, get the :class:`Track` object for ``refGene``:

.. doctest::

    >>> t = u.tracks['refGene']

The :attr:`Track.url` attribute points to the track's configuration page:

.. doctest::

    >>> print t.url
    http://genome.ucsc.edu/cgi-bin/../cgi-bin/hgTrackUi?hgsid=...&c=chr1&g=refGene

.. note::

    If you're running the code yourself, the session ID (``hgsid``)
    is embedded in the URL, and you can just paste that link into your browser.
    But if you're just reading along then you can take a look at this generic
    URL to see the config controls:
    http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=refGene.

The configuration page is parsed with `mechanize
<http://wwwsearch.sourceforge.net/mechanize/>`_, and the forms on the page are
extracted into a list.  Since the ``refGene`` track has relatively simple
config options, we only have one form to worry about:

.. doctest::

    >>> config = t.config
    >>> print config.forms
    [<mechanize._form.HTMLForm instance at 0x...>]

To figure out how to interact with the form, it's generally a good idea to just
print it to see what kind of controls it has.  The
:meth:`ConfigPage.print_forms` method is great for this -- and it ignores the
hidden controls and the submit button in the form, which aren't used for
configuration.

.. doctest::

    >>> config.print_forms()
    forms[0]
       <SelectControl(refGene=[hide, *dense, squish, pack, full])>
       <CheckboxControl(refGene.label.gene=[*on])>
       <CheckboxControl(refGene.label.acc=[on])>
       <CheckboxControl(refGene.label.omimhg19=[on])>
       <CheckboxControl(refGene.hideNoncoding=[on])>
       <SelectControl(refGene.baseColorDrawOpt=[*none, genomicCodons])>
       <CheckboxControl(refGene.codonNumbering=[(on)])>

The "*" shows indicates which choice is selected, and other choices are
displayed.  The form is accessed like a dictionary, and checkbox and select
controls are provided with a single-item list.  An example is probably best;
here we set the visibility to "pack" and enable all the checkboxes:

.. doctest::

    >>> form = config.forms[0]
    >>> form['refGene'] = ['pack']
    >>> form['refGene.label.gene'] = ['on']
    >>> form['refGene.label.acc'] = ['on']
    >>> form['refGene.label.omimhg19'] = ['on']

Printing the form shows the updated settings:

.. doctest::

    >>> config.print_forms()
    forms[0]
       <SelectControl(refGene=[hide, dense, squish, *pack, full])>
       <CheckboxControl(refGene.label.gene=[*on])>
       <CheckboxControl(refGene.label.acc=[*on])>
       <CheckboxControl(refGene.label.omimhg19=[*on])>
       <CheckboxControl(refGene.hideNoncoding=[on])>
       <SelectControl(refGene.baseColorDrawOpt=[*none, genomicCodons])>
       <CheckboxControl(refGene.codonNumbering=[(on)])>

The choices with "*" now reflect the changes.  After making all the config
changes, call the config.submit() method and then check out the results in your
web browser:

.. doctest::

    >>> config.submit()
    <Response [200]>

.. doctest::

    >>> u.show()
    <Response [200]>


Changing genomes
----------------
You can change genomes to any assembly supported by the mirror you are
connected to; simply use the :meth:`UCSCSession.change_genome` method:

.. doctest::

    >>> u.set_genome('dm3')
    <Response [200]>


.. doctest::

    >>> u.show()
    <Response [200]>

Of course, this now has an entirely new set of tracks to work with; for example
there's a FlyBase track for the Drosophila assembly:

.. doctest::

    >>> print u.tracks['flyBaseGene']
    <Track "flyBaseGene" (FlyBase Genes) [pack]>
