from collections import defaultdict
import argparse
import json
import re
from bs4 import BeautifulSoup

"""
Read site.do\?siteId\=N files resulting from wget and extract out a dictionary suitable
for importing as a fixture

Article titles are in the <title> element

Authors are in <div id='author-names'><span>author1</span><span>author2</span></div> 

Journal and article links may be in 
<div id='journal'>
  <span>some text</span>
  <a href="#abstract-paper-N">Abstract</a>
  <a href="someurl" target="_blank" class="link">Paper</a>
</div>

Coders end up in bare divs inside of slides
<div id='slides'>
blahblahblah

<div style="width: 180px; float: left;">

  <img>
  <div>
    <p class='name'>
    <p class='affiliation'>
    <p class='country'>
  </div>
</div>

blahblahblah


"""

def snarf_file(fname):
    """ read file and extract data to import to the new site
    returns dictionary filled with data
    """
    # we are globbing files that are named like this: 'site.do?siteId=62'
    m = re.search(r'\d+', f)
    if m is None:
        return {}

    legacy_id = m.group()

    with open(fname) as fh:
        soup = BeautifulSoup(fh)
        d = {}
        d['title'] = soup.title.text
        d['abstract'] = get_abstract(soup, legacy_id)
        d['explanatory_text'] = get_explanatory_text(soup)
        d['names'] = get_names(soup)
        d.update(get_journal_data(soup))
        coders = get_coders(soup)
        d['coders'] = coders
        d['legacy_id'] = legacy_id
        return d

def print_usernames(fname):
    with open(fname) as fh:
        soup = BeautifulSoup(fh)
        spans = soup.select('div#author-names > span')
        for n in spans:
            print re.sub(r'\s+|\.|-', '', n.text).strip()


def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def get_coders(soup):
    """ extracts coder information in to a dict of dicts for each coder """

    # grabs a list of divs, some of them have redundent info
    coderdivs = soup.find_all("div", style="width: 180px; float: left;")
    coders = defaultdict(dict)
    for div in coderdivs:
        names = div.select('p.name')
        if len(names) == 0:
            continue
        name = clean_text(names[0].text)
        if name in coders:
            continue
        affiliations = div.select('p.affiliation')
        countrys = div.select('p.country')
        if len(affiliations) > 0:
            coders[name]['affiliation'] = clean_text(affiliations[0].text)
        if len(countrys) > 0:
            coders[name]['country'] = clean_text(countrys[0].text)
    return coders


def get_names(soup):
    spans = soup.select('div#author-names > span')
    names = []
    for n in spans:
        names.append(clean_text(n.text))
    return names


def get_journal_data(soup):
    d = {}
    journalsoup = soup.select('div#journal > span')
    if len(journalsoup) == 0:
        return d
    journal = journalsoup[0]
    d['journal'] = clean_text(journal.text)

    links = journal.select('a')
    for link in links:
        m = re.search(r'abstract-paper-(?P<legacyid>\d+)', link['href'])
        if m:
            d['legacyid'] = m.group('legacyid')
        else:
            d['article_url'] = link['href']
    return d


def get_abstract(soup, legacy_id):
    abstract_results = soup.select('div#abstract-paper-'+legacy_id+' > div.middle-abstract-paper')
    if len(abstract_results):
        return clean_text(abstract_results[0].text)
    return ''


def get_explanatory_text(soup):
    # there should be only one abstract, stop at the first result
    abstract_results = soup.find_all(id='top-resume-code', limit=1)
    if len(abstract_results):
        return clean_text(abstract_results[0].text)
    return ''
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='snarf files from wget results and extract info')
    parser.add_argument('files', metavar='N', nargs='+')
    args = parser.parse_args()
    datalist = []
    for f in args.files:
        d = snarf_file(f)
        datalist.append(d)

    fout = open('results.json', 'w+')
    json.dump(datalist, fout, indent=2)
    fout.close()
