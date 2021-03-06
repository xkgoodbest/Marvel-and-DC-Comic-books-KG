from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
from flask import Flask, render_template, request, redirect, Response, url_for, session, jsonify
import random
import json
import sys

SPARQL_PREFIXES = """
            prefix md: <http://www.w3.org/ns/md#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix schema: <http://schema.org/>
            prefix xml: <http://www.w3.org/XML/1998/namespace>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbp: <http://dbpedia.org/property/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix dbr: <http://dbpedia.org/resource/>
            prefix mdcu: <http://inf558.org/comics#>

            """
PREFIX_REPLACE = {
    'http://www.w3.org/ns/md#': 'md:',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf:',
    'http://www.w3.org/2000/01/rdf-schema#': 'rdfs:',
    'http://schema.org/': 'schema:',
    'http://www.w3.org/XML/1998/namespace': 'xml:',
    'http://www.w3.org/2001/XMLSchema#': 'xsd:',
    'http://xmlns.com/foaf/0.1/': 'foaf:',
    'http://dbpedia.org/property/': 'dbp:',
    'http://dbpedia.org/ontology/': 'dbo:',
    'http://dbpedia.org/resource/': 'dbr:',
    'http://inf558.org/comics#': 'mdcu:'
}
COLORS_LIST = ["#F7464A", "#46BFBD", "#FDB45C",
               "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC"]
CLASS_OPTS = ["mdcu:character", "mdcu:issue", "mdcu:movie"]
# this is used for the default view
CLASS_ATTR_BEST_OPT = {CLASS_OPTS[0]: 1,
                       CLASS_OPTS[1]: 1,
                       CLASS_OPTS[2]: 0}

app = Flask(__name__)
app.secret_key = "super secret key"
sparql = SPARQLWrapper("http://localhost:3030/mdccomics/query")
sparql.setReturnFormat(JSON)

@app.route('/')
def output():
    # take default class
    cclass = CLASS_OPTS[0]
    pred_opts = get_avilable_properties_for_class(cclass)
    # take 'default' option
    cpredicate_clean = pred_opts[CLASS_ATTR_BEST_OPT[cclass]]
    return return_main_page_with_filters(cclass, cpredicate_clean, pred_opts)

@app.route('/refreshfiltertop', methods=['GET'])
def refresh_filter_top_results():
    # chosen_class has changed, need to re-generate the form
    cclass = request.args.get('chosen_class')
    # since chose_class has change, we cannot take the 'chosen_attr', it doesn't match, take 'default' option
    pred_opts = get_avilable_properties_for_class(cclass)
    cpredicate_clean = pred_opts[CLASS_ATTR_BEST_OPT[cclass]]
    return return_main_page_with_filters(cclass, cpredicate_clean, pred_opts)

@app.route('/filtertop', methods=['GET'])
def filter_top_results():
    # take chosen class
    cclass = request.args.get('chosen_class')
    pred_opts = get_avilable_properties_for_class(cclass)
    # take chosen attribute
    cpredicate_clean = request.args.get('chosen_attr')
    return return_main_page_with_filters(cclass, cpredicate_clean, pred_opts)

@app.route('/query')
def query_no_res():
    return render_template('query.html', title='Query')

@app.route('/query', methods=['POST'])
def query():
    # read the posted values from the UI
    _sparql = request.form['sparql']
    if _sparql:
        sparql.setQuery(SPARQL_PREFIXES + _sparql)
        results = sparql.query().convert()
        ret = list()
        try:
            keys = results["results"]["bindings"][0].keys()
            for i in range(len(results["results"]["bindings"])):
                re = list()
                for k in keys:
                    if results["results"]["bindings"][i][k]['type'] == 'uri':
                        replaced_uri = add_prefix(
                            results["results"]["bindings"][i][k]['value'])
                        actual_link = True if (
                            'https://' in replaced_uri or 'http://' in replaced_uri) else False
                        re.append((replaced_uri, True, actual_link))
                    else:
                        re.append(
                            (results["results"]["bindings"][i][k]['value'], False, False))
                ret.append(re)
        except:
            keys = ['No results']
        return render_template('query.html', title='Query', key=keys, result=ret)

@app.route('/description', methods=['GET', 'POST'])
def description():
    uri = request.args.get('uri')
    hexvals_of_colors = get_image_and_colors_if_class_is_character(uri)
    keys_result = ['subject', 'predicate', 'object']
    ret = get_all_attr(uri)
    return render_template('description.html', key=keys_result, result=ret,
                           requri=uri, colorsvals=hexvals_of_colors)

def add_prefix(uri):
    for key in PREFIX_REPLACE.keys():
        if key in uri:
            uri = uri.replace(key, PREFIX_REPLACE[key])
            return uri
    return uri


def get_image_and_colors_if_class_is_character(uri):
    hex_vals = []
    _sparql = """
            SELECT ?hexval
            WHERE {
              %s a mdcu:character ;
                    mdcu:has_color [ mdcu:hex_val ?hexval ] .
            }
            """ % (uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql)
    results = sparql.query().convert()

    if len(results["results"]["bindings"]) == 0:
        return hex_vals

    keys = results["results"]["bindings"][0].keys()
    int_results = results["results"]["bindings"]
    for i in range(len(int_results)):
        for k in keys:
            curr_val = int_results[i][k]['value']
            hex_vals.append(curr_val)
    return hex_vals


def get_all_attr(uri):
    ret = list()
    key1 = ['predicate', 'object']
    _sparql1 = """
            SELECT  ?predicate ?object
            WHERE {
              %s ?predicate ?object .
            }
            LIMIT 200
            """ % (uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql1)
    results = sparql.query().convert()
    if results["results"]["bindings"]:
        for i in range(len(results["results"]["bindings"])):
            re = list()
            replaced_uri = add_prefix(uri)
            actual_link = True if (
                'https://' in replaced_uri or 'http://' in replaced_uri) else False
            re.append((replaced_uri, True, actual_link))
            for k in key1:
                if results["results"]["bindings"][i][k]['type'] == 'uri':
                    replaced_uri = add_prefix(
                        results["results"]["bindings"][i][k]['value'])
                    actual_link = True if (
                        'https://' in replaced_uri or 'http://' in replaced_uri) else False
                    re.append((replaced_uri, True, actual_link))
                else:
                    re.append(
                        (results["results"]["bindings"][i][k]['value'], False, False))
            ret.append(re)

    _sparql2 = """
            SELECT  ?subject ?object
            WHERE {
              ?subject %s ?object .
            }
            LIMIT 200
            """ % (uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql2)
    results = sparql.query().convert()
    if results["results"]["bindings"]:
        for i in range(len(results["results"]["bindings"])):
            re = list()
            if results["results"]["bindings"][i]['subject']['type'] == 'uri':
                replaced_uri = add_prefix(
                    results["results"]["bindings"][i]['subject']['value'])
                actual_link = True if (
                    'https://' in replaced_uri or 'http://' in replaced_uri) else False
                re.append((replaced_uri, True, actual_link))
            else:
                re.append((results["results"]["bindings"]
                           [i]['subject']['value'], False, False))
            replaced_uri = add_prefix(uri)
            actual_link = True if (
                'https://' in replaced_uri or 'http://' in replaced_uri) else False
            re.append((replaced_uri, True, actual_link))
            if results["results"]["bindings"][i]['object']['type'] == 'uri':
                replaced_uri = add_prefix(add_prefix(
                    results["results"]["bindings"][i]['object']['value']))
                actual_link = True if (
                    'https://' in replaced_uri or 'http://' in replaced_uri) else False
                re.append((replaced_uri, True, actual_link))
            else:
                re.append((results["results"]["bindings"]
                           [i]['object']['value'], False, False))
            ret.append(re)
    key3 = ['subject', 'predicate']
    _sparql3 = """
            SELECT  ?subject ?predicate
            WHERE {
              ?subject ?predicate %s .
            }
            LIMIT 200
            """ % (uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql3)
    results = sparql.query().convert()
    if results["results"]["bindings"]:
        for i in range(len(results["results"]["bindings"])):
            re = list()
            for k in key3:
                if results["results"]["bindings"][i][k]['type'] == 'uri':
                    replaced_uri = add_prefix(add_prefix(
                        results["results"]["bindings"][i][k]['value']))
                    actual_link = True if (
                        'https://' in replaced_uri or 'http://' in replaced_uri) else False
                    re.append((replaced_uri, True, actual_link))
                else:
                    re.append(
                        (results["results"]["bindings"][i][k]['value'], False, False))
            replaced_uri = add_prefix(uri)
            actual_link = True if (
                'https://' in replaced_uri or 'http://' in replaced_uri) else False
            re.append((replaced_uri, True, actual_link))
            ret.append(re)
    return ret

def return_main_page_with_filters(cclass, cpredicate_clean, pred_opts):
    cpredicate = '<' + cpredicate_clean + '>'
    labels, values = get_top_labels_values_for_class_predicate(
        cclass, cpredicate)
    max_val = cast_and_find_max(values)
    return render_template('index.html', chart_viz=True,
                           classdropdown=CLASS_OPTS, attrdropdown=pred_opts,
                           selectedclass=cclass, selectedattr=cpredicate_clean,
                           set=zip(values, labels, COLORS_LIST), values=values, labels=labels, max_val=max_val)


def get_top_labels_values_for_class_predicate(class_uri, predicate_uri):
    _sparql = """
            SELECT ?var (count(?subject) as ?count)
            WHERE {
              ?subject a %s ;
                       %s ?var .
            }
            GROUP BY ?var
            ORDER BY DESC(?count)
            LIMIT 10
            """ % (class_uri, predicate_uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql)
    results = sparql.query().convert()
    keys = results["results"]["bindings"][0].keys()
    int_results = results["results"]["bindings"]
    labels, values = [], []
    for i in range(len(int_results)):
        for k in keys:
            curr_val = int_results[i][k]['value']
            if k == 'var':
                replaced_uri = add_prefix(curr_val)
                is_uri = True if (
                    'https://' in curr_val or 'http://' in curr_val) else False
                actual_link = True if len(
                    replaced_uri) == len(curr_val) else False
                labels.append((replaced_uri, is_uri, actual_link))
            else:
                values.append(curr_val)
    return labels, values

def get_avilable_properties_for_class(class_uri):
    _sparql = """
            SELECT DISTINCT ?predicate
            WHERE {
              ?subject a %s ;
                       ?predicate ?var .
              FILTER NOT EXISTS {
                FILTER regex(str(?predicate), "relative")
              }
            }
            """ % (class_uri)
    sparql.setQuery(SPARQL_PREFIXES + _sparql)
    results = sparql.query().convert()
    keys = results["results"]["bindings"][0].keys()
    int_results = results["results"]["bindings"]

    predicates = []
    for i in range(len(int_results)):
        for k in keys:
            curr_val = int_results[i][k]['value']
            predicates.append(curr_val)

    return predicates

def cast_and_find_max(strlist):
    max_val = 0
    for currstr in strlist:
        currnum = int(currstr)
        if currnum > max_val:
            max_val = currnum
    return max_val

if __name__ == '__main__':
    app.run(debug=True)
