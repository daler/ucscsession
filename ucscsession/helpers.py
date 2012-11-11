import os
import webbrowser
from bs4 import BeautifulSoup

def view_response(response):
    fout = open('tmp.html', 'w')
    fout.write(response.content)
    fout.close()
    webbrowser.open('tmp.html')


def hgsid_from_response(r):
    soup = BeautifulSoup(r.text)
    hgsid = set([i.get('value') for i in soup('input', dict(name='hgsid'))])
    assert len(hgsid) == 1
    hgsid = list(hgsid)[0]
    return hgsid


def pprint(response):
    b = BeautifulSoup(response.text)
    print b.prettify()


def pdf_link(response):
    b = BeautifulSoup(response.text)
    links = b('a')
    for i in links:
        fn = i['href']
        if ('hgt_genome_' in fn) and (fn.endswith('.pdf')):
            return os.path.join(os.path.dirname(response.url), fn)
