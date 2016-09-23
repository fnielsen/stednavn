#!/usr/bin/env python
"""Stednavn.

Usage:
  stednavn [options] <filename>

Options:
  -h --help  Help message


Description
-----------

The Wikidata SPARQL to obtain placenames:

PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX q: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?place ?placeLabel WHERE {
   ?place wdt:P17 wd:Q35 .
   ?place wdt:P625 ?geo .
   SERVICE wikibase:label { bd:serviceParam wikibase:language "da" . }
 }

"""

from __future__ import absolute_import, division, print_function

import codecs

from os.path import dirname, join

import pandas as pd

import re


class Stednavn(object):
    """Extractor of placenames."""

    def __init__(self, language="da"):
        self.setup_placenames()
        self.setup_pattern()
        
    def setup_placenames(self):
        """Read placename data from data file.

        This function relies on a file with placenames.
        It sets up the `placenames` attribute.

        """
        filename = join(dirname(__file__), 'data', 'stednavne.tsv')
        placename_data = pd.read_csv(filename, sep='\t', encoding='utf-8')
        self.placenames = []                         
        for placename in placename_data['?placeLabel'].values:
            if placename.endswith('@da'):
                placename = placename[:-3]
                index = placename.find(' (')
                if index != -1:
                    placename = placename[:index]
                self.placenames.append(placename)

    def setup_pattern(self):
        """Setup regular expression for placename matching.

        This method sets up the `pattern` attribute with compiled
        regular expression.

        This is called during initialization, and can be called again if 

        """
        self.placenames.sort(key=lambda placename: len(placename), reverse=True)
        # Build regular expression
        tokens = [re.escape(placename) for placename in self.placenames]
        regexp = r'(\b(?:' + r"|".join(tokens) + r')\b)'
        self.pattern = re.compile(regexp, flags=re.UNICODE)

    def extract_placenames(self, filename, encoding='utf-8'):
        """Extract placenames for file.

        Parameters
        ----------
        filename : str
            Filename for text where placenames should be extracted.

        Returns
        -------
        placenames : list of str
            List of strings representing placenames.

        """
        with codecs.open(filename, encoding=encoding) as fid:
            text = fid.read()
            text = re.sub('\n', ' ', text)

        matches = self.pattern.findall(text)
        return matches


def main():
    """Command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)
    stednavn = Stednavn()
    placenames = stednavn.extract_placenames(arguments['<filename>'])
    print("\n".join(placenames))


if __name__ == '__main__':
    main()
