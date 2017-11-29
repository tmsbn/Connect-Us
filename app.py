"""
file: app.py
author: Kritka Sahni, Jitesh Fulwariya, Palash Kumar Koutu, Thomas Binu
Description: This file contains API end-points which can be hit by front-end. These
end-points contains various queries to be executed on Neo4j database.
"""

# import statements here
from flask import Flask, g, Response, request, jsonify, render_template
from neo4j.v1 import GraphDatabase, basic_auth
from json import dumps
import logging

app = Flask(__name__, static_url_path='/static/')

driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "root"))

logging.basicConfig(level=logging.DEBUG)


# Get the index file
@app.route("/")
def get_index():
    return render_template('index.html')


# Serialize person and company as together in object
def serialize_person_and_company(record, person_key='person', company_key='company'):
    person = record[person_key]
    company = record[company_key]

    return {
        'name': person['name'],
        'position': person['position'],
        'company': company['name']
    }


# Serialize person object
def serialize_person(person):
    return {
        'name': person['name'],
        'position': person['position'],
    }


# Serialize Company object
def serialize_company(company):
    return {
        'name': company['name'],
        'location': company['location'],
    }


# Serialize Company and openings in one object
def serialize_company_and_openings(record, company_key = 'companyName', openings_key = 'jobs'):
    company_name = record[company_key]
    openings = record[openings_key]
    return{
        'name': company_name,
        'openings': ",".join(openings),   
    }
   

# Get graph db
def get_session():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_session = driver.session()
    return g.neo4j_session


# Close graph db
@app.teardown_appcontext
def close_session(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_session.close()


# Search for company
@app.route("/allcompanies")
def get_all_companies():
    db_session = get_session()
    res = db_session.run("MATCH (company:COMPANY) " +
                             "RETURN company")

    return Response(dumps([serialize_company(record['company']) for record in res]),
                    mimetype="application/json")


# Search for company
@app.route("/searchcompany")
def search_company():
    try:
        company_search = request.args["company"]
    except KeyError:
        return Response(dumps([]))
    else:
        db_session = get_session()
        res = db_session.run("MATCH (company:COMPANY) " +
                                 "WHERE company.name =~ {name} " +
                                 "RETURN company", 
                                 {"name": "(?i).*" + company_search + ".*"})
        return Response(dumps([serialize_company(record['company']) for record in res]),
                        mimetype="application/json")


# Search for company
@app.route("/hello")
def hello():
    return jsonify({'hello': 'world'})


# get connections of person
@app.route("/connections")
def search_connections():
    try:
        person_search = request.args["person"]
    except KeyError:
        return Response(dumps([]))
    else:
        db_session = get_session()

        query = 'MATCH (person:PERSON)-[r:CONNECTED_TO]-(connection:PERSON), ' + \
                '(company:COMPANY) WHERE person.name =~ {name} AND (connection)-[:WORKS_IN]-(company:COMPANY) ' + \
                'return connection, company'
        res = db_session.run(query, {"name": "(?i).*" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record, person_key='connection') for record in res]),
                        mimetype="application/json")


# suggest connections
@app.route("/suggestconnections")
def suggest_connections():
    try:
        person_search = request.args["person"]
    except KeyError:
        return Response(dumps([]))
    else:
        db_session = get_session()
        res = db_session.run("MATCH (personA:PERSON)-[:WORKED_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKED_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB, company UNION " +

                                 "MATCH (personA:PERSON)-[:WORKS_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKED_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB, company UNION " +

                                 "MATCH (personA:PERSON)-[:WORKED_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKS_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB, company UNION " +

                                 "MATCH (personA:PERSON)-[:WORKS_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKS_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB, company LIMIT 5", 
                                 {"name": "(?i).*" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record, person_key='personB') for record in res]),
                        mimetype="application/json")


# suggest companies
@app.route("/suggestcompanies")
def suggest_companies():
    try:
        person_search = request.args["person"]
    except KeyError:
        return Response(dumps([]))
    else:
        db_session = get_session()
        res = db_session.run("MATCH (person:PERSON), (company:COMPANY) WITH company, " + 
                                 "filter(opening IN company.openings WHERE opening CONTAINS " + 
                                 "split(person.position,' -')[0]) AS jobs WHERE person.name =~ {name} " + 
                                 "AND NOT (person)-[:WORKS_IN]-(company) AND NOT size(jobs) = 0 RETURN " +
                                 "company.name AS companyName, jobs", 
                                 {"name": "(?i).*" + person_search + ".*"})
        return Response(dumps([serialize_company_and_openings(record, company_key = 'companyName', openings_key = 'jobs')\
                        for record in res]),
                        mimetype="application/json")


# Search for person and return details
@app.route("/searchperson")
def search_person():
    try:
        person_search = request.args["person"]
    except KeyError:
        return Response(dumps([]))
    else:
        db_session = get_session()

        res = db_session.run("MATCH (person:PERSON)-[:WORKS_IN]-(company:COMPANY)  " +
                                 "WHERE person.name =~ {name} " +
                                 "RETURN person, company", 
                                 {"name": "(?i).*" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record) for record in res]),
                        mimetype="application/json")

# Return graph in form of collections to print.
@app.route("/graph")
def get_graph():
    db = get_session()
    person_search = request.args["person"]
    res = db.run("MATCH (person:PERSON), (company:COMPANY) WITH company, " +
                                 "filter(opening IN company.openings WHERE opening CONTAINS " +
                                 "split(person.position,' -')[0]) AS jobs WHERE person.name =~ {name} " +
                                 "AND NOT (person)-[:WORKS_IN]-(company) AND NOT size(jobs) = 0 RETURN " +
                                 "company.name AS companyName, jobs",
                                 {"name": "(?i).*" + person_search + ".*"})
    nodes = []
    relations = []
    i = 0
    for record in res:
        nodes.append({"person": record["company"], "label": "company"})
        to = i
        i += 1
        for name in record['persom']:
            actor = {"person": name, "label": "person"}
            try:
                src = nodes.index(person_search)
            except ValueError:
                nodes.append(person_search)
                src = i
                i += 1
            relations.append({"src": src, "to": to})
    return Response(dumps({"nodes": nodes, "links": relations}),
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(port=8888, debug=True, use_reloader=True)
