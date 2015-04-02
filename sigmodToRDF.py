#! /usr/bin/python
# -*- coding:utf8 -*-

"""
    sigmodToRDF.py
    Par Guillaume Lahaie
    Premier essai d'extraire les informations de la table des matières de
    la page d'une conférence de sigmod et d'en faire un document RDF.
"""

import urllib2
from lxml import etree
from lxml import html
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import DC, RDF, FOAF

SIGMOD_2014_URL = "http://dl.acm.org/citation.cfm?id=2588555&preflayout=flat"

ACM_PREFIX_URL = "http://dl.acm.org/"

#graph
graph = Graph()

sigmod_page = html.parse(SIGMOD_2014_URL)

sigmod_uri = URIRef(SIGMOD_2014_URL)


#First, let's get the year of the conference
year = [int(s) for s in sigmod_page.xpath('//h1[@class="mediumb-text"]/strong')[0].text.split() if s.isdigit()][0]
print "sigmod year = " + str(year)

year_lit = Literal(year)

graph.add( (sigmod_uri, DC.date, year_lit) )

#TODO - identify the chairs

start_writing_authors = False
article_uri = None
#extact the articles - if the href contains citation, then it's a new article, we create a new entry
#and then add the author
for link in sigmod_page.iter('a'):
    if 'href' in link.keys():
        if 'citation' in link.attrib['href']:
            #check if it refers to previous proceedings
            if 'title' in link.keys():
                start_writing_authors = True
                #TODO: get the url of previous proceedings, make a loop of this
            else:
                #Create a new article entry - the title and the conference it's related to
                article_uri = URIRef(ACM_PREFIX_URL+link.attrib['href'])
                title = Literal(link.text)
                graph.add( (article_uri, DC.title, title) )
                graph.add( (article_uri, DC.relation, sigmod_uri) )
        if 'author_page' in link.attrib['href'] and start_writing_authors and article_uri is not None:
            author_uri = URIRef(ACM_PREFIX_URL+link.attrib['href'])
            graph.add( (article_uri, DC.creator, author_uri) )
            author_name = Literal(link.text)
            graph.add( (author_uri, FOAF.name, author_name) )

print graph.serialize()
