from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
from flask import Flask, render_template, request, redirect, Response, url_for, session, jsonify
import random
import json
import sys

app = Flask(__name__)
app.secret_key = "super secret key"
sparql = SPARQLWrapper("http://localhost:3030/mdccomics/query")
sparql.setReturnFormat(JSON)

@app.route('/')
def output():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():

    # read the posted values from the UI
    _sparql = request.form['sparql']
    print(_sparql)
    if _sparql :
        sparql_q_pre = """
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
        sparql.setQuery(sparql_q_pre + _sparql)
        results = sparql.query().convert()
        keys=results["results"]["bindings"][0].keys()
        ret=list()
        for i in range(len(results["results"]["bindings"])):
            re=list()
            for k in keys:
                re.append(results["results"]["bindings"][i][k]['value'])
            ret.append(re)
        return render_template('index.html', key=keys,result=ret)

if __name__ == '__main__':
    app.run(debug=True)


