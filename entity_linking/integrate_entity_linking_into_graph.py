import json
import rdflib
import calendar
import re
import pprint
from rdflib import Graph
from rdflib import BNode, URIRef, Literal, XSD, Namespace, RDF, RDFS

# Load ER json dicts
# MOVIE_CHARS_DICT --> WIKIA_CHARS_DICT
# ISSUE_CHARS_DICT --> WIKIA_CHARS_DICT
SIM_CHARS__MOVIE_TO_WIKIA = json.load(open('SIM_CHARS__MOVIE_TO_WIKIA.json', "r"))
FURI_SIM_CHARS__MOVIE_TO_WIKIA = dict()
SIM_CHARS__ISSUE_TO_WIKIA = json.load(open('SIM_CHARS__ISSUE_TO_WIKIA.json', "r"))
FURI_SIM_CHARS__ISSUE_TO_WIKIA = dict()
# ISSUE_TEAMS_DICT --> WIKIA_TEAMS_DICT
SIM_TEAMS__ISSUE_TO_WIKIA = json.load(open('SIM_TEAMS__ISSUE_TO_WIKIA.json', "r"))
FURI_SIM_TEAMS__ISSUE_TO_WIKIA = dict()
# ISSUE_LOCATIONS_DICT --> WIKIA_LOCATIONS_DICT
SIM_LOCATIONS__ISSUE_TO_WIKIA = json.load(open('SIM_LOCATIONS__ISSUE_TO_WIKIA.json', "r"))
FURI_SIM_LOCATIONS__ISSUE_TO_WIKIA = dict()

def get_uriref_from_str(uristring):
    return URIRef(MDCU[uristring.split('mdcu:')[1]])

def create_new_fulluri_dicts():
    for key, items in SIM_CHARS__MOVIE_TO_WIKIA.items():
        uriref_key = get_uriref_from_str(key)
        uriref_val = get_uriref_from_str(items[0])
        FURI_SIM_CHARS__MOVIE_TO_WIKIA[uriref_key] = uriref_val
    for key, items in SIM_CHARS__ISSUE_TO_WIKIA.items():
        uriref_key = get_uriref_from_str(key)
        uriref_val = get_uriref_from_str(items[0])
        FURI_SIM_CHARS__ISSUE_TO_WIKIA[uriref_key] = uriref_val
    for key, items in SIM_TEAMS__ISSUE_TO_WIKIA.items():
        uriref_key = get_uriref_from_str(key)
        uriref_val = get_uriref_from_str(items[0])
        FURI_SIM_TEAMS__ISSUE_TO_WIKIA[uriref_key] = uriref_val
    for key, items in SIM_LOCATIONS__ISSUE_TO_WIKIA.items():
        uriref_key = get_uriref_from_str(key)
        uriref_val = get_uriref_from_str(items[0])
        FURI_SIM_LOCATIONS__ISSUE_TO_WIKIA[uriref_key] = uriref_val

def er_uri_fix(olduri):
    if olduri in FURI_SIM_CHARS__MOVIE_TO_WIKIA:
        return FURI_SIM_CHARS__MOVIE_TO_WIKIA[olduri]
    elif olduri in FURI_SIM_CHARS__ISSUE_TO_WIKIA:
        return FURI_SIM_CHARS__ISSUE_TO_WIKIA[olduri]
    elif olduri in FURI_SIM_TEAMS__ISSUE_TO_WIKIA:
        return FURI_SIM_TEAMS__ISSUE_TO_WIKIA[olduri]
    elif olduri in FURI_SIM_LOCATIONS__ISSUE_TO_WIKIA:
        return FURI_SIM_LOCATIONS__ISSUE_TO_WIKIA[olduri]
    else:
        return olduri

# Namespaces
SCHEMA = Namespace('http://schema.org/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DBP = Namespace('http://dbpedia.org/property/')
DBO = Namespace('http://dbpedia.org/ontology/')
DBR = Namespace('http://dbpedia.org/resource/')
MDCU = Namespace('http://inf558.org/comics#')

# Load ER json dicts
# MOVIE_CHARS_DICT --> WIKIA_CHARS_DICT
# ISSUE_CHARS_DICT --> WIKIA_CHARS_DICT
SIM_CHARS__MOVIE_TO_WIKIA = json.load(open('SIM_CHARS__MOVIE_TO_WIKIA.json', "r"))
SIM_CHARS__ISSUE_TO_WIKIA = json.load(open('SIM_CHARS__ISSUE_TO_WIKIA.json', "r"))
# ISSUE_TEAMS_DICT --> WIKIA_TEAMS_DICT
SIM_TEAMS__ISSUE_TO_WIKIA = json.load(open('SIM_TEAMS__ISSUE_TO_WIKIA.json', "r"))
# ISSUE_LOCATIONS_DICT --> WIKIA_LOCATIONS_DICT
SIM_LOCATIONS__ISSUE_TO_WIKIA = json.load(open('SIM_LOCATIONS__ISSUE_TO_WIKIA.json', "r"))

create_new_fulluri_dicts()

# Load Old Graph
g = Graph()
g.parse("mdc_comics.no_er.ttl", format="turtle")
g.bind('schema', SCHEMA)
g.bind('foaf', FOAF)
g.bind('dbp', DBP)
g.bind('dbo', DBO)
g.bind('dbr', DBR)
g.bind('mdcu', MDCU)

fg = g

# Iterate over all triples
for (s, p, o) in g:
    fg.remove( (s, p, o) )
    fg.add( (er_uri_fix(s), p, er_uri_fix(o)) )

print('Old graph had %d triples --> New graph has %d' % (len(g), len(fg)))

fg.serialize("mdc_comics.ttl", format="turtle")

'''
for key, items in SIM_CHARS__MOVIE_TO_WIKIA.items():
    print('%s --> %s' % (key, items[0]))
    uriref_key = get_uriref_from_str(key)
    uriref_val = get_uriref_from_str(items[0])
    print('%s --> %s' % (uriref_key, uriref_val))
    break
for key, items in SIM_CHARS__ISSUE_TO_WIKIA.items():
    print('%s --> %s' % (key, items[0]))
    uriref_key = get_uriref_from_str(key)
    uriref_val = get_uriref_from_str(items[0])
    print('%s --> %s' % (uriref_key, uriref_val))
    break
for key, items in SIM_TEAMS__ISSUE_TO_WIKIA.items():
    print('%s --> %s' % (key, items[0]))
    uriref_key = get_uriref_from_str(key)
    uriref_val = get_uriref_from_str(items[0])
    print('%s --> %s' % (uriref_key, uriref_val))
    break
for key, items in SIM_LOCATIONS__ISSUE_TO_WIKIA.items():
    print('%s --> %s' % (key, items[0]))
    uriref_key = get_uriref_from_str(key)
    uriref_val = get_uriref_from_str(items[0])
    print('%s --> %s' % (uriref_key, uriref_val))
    break
'''
