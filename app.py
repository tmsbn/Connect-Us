import os
from flask import Flask, g, Response, request, jsonify, render_template
from neo4j.v1 import GraphDatabase, basic_auth
from json import dumps
import logging

app = Flask(__name__, static_url_path='/static/')

driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "neo4j"))

logging.basicConfig(level=logging.DEBUG)

print('hello world')


# Get the index file
@app.route("/")
def get_index():
    return render_template('index.html')


# Serialize person object
def serialize_person_and_company(record, person_key='person', company_key='company'):
    person = record[person_key]
    company = record[company_key]

    return {
        'name': person['name'],
        'position': 'Software Engineer',
        'company': company['name']
    }


# Serialize person object
def serialize_person(person):
    return {
        'name': person['name'],
        'position': 'Software Engineer',
    }


# Serialize Company object
def serialize_company(company):
    return {
        'name': company['name'],
        'location': 'seattle',
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
    results = db_session.run("MATCH (company:COMPANY) " +
                             "RETURN company")

    return Response(dumps([serialize_company(record['company']) for record in results]),
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
        results = db_session.run("MATCH (company:COMPANY) " +
                                 "WHERE company.name =~ {name} " +
                                 "RETURN company"
                                 , {"name": "(?i)" + company_search + ".*"})
        return Response(dumps([serialize_company(record['company']) for record in results]),
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

        query = 'MATCH (person:PERSON {name:{name}})-[r]-(connection:PERSON), (company:COMPANY) WHERE (connection)-[:WORKS_IN]-(company:COMPANY) return connection, company'
        results = db_session.run(query, {"name": person_search})
        return Response(dumps([serialize_person_and_company(record, person_key='connection') for record in results]),
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
        results = db_session.run("MATCH (personA:PERSON)-[:WORKED_IN]-(company:COMPANY), (personB:PERSON) " +
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
                                 "return personB, company LIMIT 5", {"name": "(?i)" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record, person_key='personB') for record in results]),
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
        results = db_session.run("MATCH (personA:PERSON)-[:WORKED_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKED_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB UNION " +

                                 "MATCH (personA:PERSON)-[:WORKS_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKED_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB UNION " +

                                 "MATCH (personA:PERSON)-[:WORKED_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKS_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB UNION " +

                                 "MATCH (personA:PERSON)-[:WORKS_IN]-(company:COMPANY), (personB:PERSON) " +
                                 "WHERE personA.name =~ {name} AND " +
                                 "(personB)-[:WORKS_IN]-(company:COMPANY) AND " +
                                 "personB <> personA AND NOT (personB)-[:CONNECTED_TO]-(personA) " +
                                 "return personB, company", {"name": "(?i)" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record['personB']) for record in results]),

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

        results = db_session.run("MATCH (person:PERSON)-[:WORKS_IN]-(company:COMPANY)  " +
                                 "WHERE person.name =~ {name} " +
                                 "RETURN person, company"
                                 , {"name": "(?i)" + person_search + ".*"})
        return Response(dumps([serialize_person_and_company(record) for record in results]),
                        mimetype="application/json")


@app.route("/graph")
def get_graph():
    db = get_session()
    pass


if __name__ == '__main__':
    app.run(port=8888, debug=True, use_reloader=True)
