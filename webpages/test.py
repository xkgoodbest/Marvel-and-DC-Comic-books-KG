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
COLORS_LIST = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"]

app = Flask(__name__)
app.secret_key = "super secret key"
sparql = SPARQLWrapper("http://localhost:3030/mdccomics/query")
sparql.setReturnFormat(JSON)

@app.route('/')
def output():
    pred_char = get_avilable_properties_for_class("mdcu:character")
    #labels, values = get_top_labels_values_for_class_predicate("mdcu:character", "dbp:publisher")

    labels, values = get_top_labels_values_for_class_predicate("mdcu:character", "schema:birthPlace")
    max_val = max(values)
    colors = COLORS_LIST
    return render_template('index.html', chart_viz=True, set=zip(values, labels, colors), values=values, labels=labels, max_val=max_val)

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
        keys=results["results"]["bindings"][0].keys()
        ret=list()
        for i in range(len(results["results"]["bindings"])):
            re=list()
            for k in keys:
                if results["results"]["bindings"][i][k]['type']=='uri':
                    re.append((results["results"]["bindings"][i][k]['value'],True))
                else:
                    re.append((results["results"]["bindings"][i][k]['value'],False))
            ret.append(re)
        return render_template('query.html', title='Query', key=keys, result=ret)

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
    print(_sparql)
    sparql.setQuery(SPARQL_PREFIXES + _sparql)
    results = sparql.query().convert()
    keys = results["results"]["bindings"][0].keys()
    int_results = results["results"]["bindings"]
    labels, values = [], []
    for i in range(len(int_results)):
        for k in keys:
            curr_val = int_results[i][k]['value']
            if k == 'var':
                labels.append(curr_val)
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

# TODO: avoid error in case of no results...

if __name__ == '__main__':
    app.run(debug=True)
