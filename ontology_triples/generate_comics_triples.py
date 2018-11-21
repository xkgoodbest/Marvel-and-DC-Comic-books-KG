import json
import rdflib
import calendar
import re
from rdflib import BNode, URIRef, Literal, XSD, Namespace, RDF, RDFS

DC_COMICS_PUB_ID = '_dc-comics_4010-10_'
MARVEL_PUB_ID = '_marvel_4010-31_'
IN_TO_CM = 2.54
FT_TO_CM = 30.48
month_to_num = {v: k for k,v in enumerate(calendar.month_name)}

SCHEMA = Namespace('http://schema.org/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DBP = Namespace('http://dbpedia.org/property/')
DBO = Namespace('http://dbpedia.org/ontology/')
DBR = Namespace('http://dbpedia.org/resource/')
MDCU = Namespace('http://inf558.org/comics#')

def compile_string_as_uri(ustring):
    u1string = ustring.replace('/', '_').replace(' ', '_').replace('-', '_').replace(',', '_').lower()
    return re.sub('\(.*?\)', '', u1string)

def curate_comicvine_date_field(string_date_field):
    str_split_by_space = string_date_field.split(' ')
    date_month = str_split_by_space[0].strip()
    date_year = '1900'
    date_day = 1
    if 2 == len(str_split_by_space):
        date_year = str_split_by_space[1].strip()
    elif 3 == len(str_split_by_space):
        date_year = str_split_by_space[2].strip()
        date_day = int(str_split_by_space[1].split(',')[0].strip())
    for month, num in month_to_num.items():
        if num == 0:
            continue
        if month.lower() in date_month.lower():
            return date_year + ('-%02d-%02d' % (num, date_day))
    return None

class ComicsGraph:
    def __init__(self):
        self.places_dict = {}
        self.triples = rdflib.Graph()
        self.triples.bind('schema', SCHEMA)
        self.triples.bind('foaf', FOAF)
        self.triples.bind('dbp', DBP)
        self.triples.bind('dbo', DBO)
        self.triples.bind('dbr', DBR)
        self.triples.bind('mdcu', MDCU)

    def add_character(self, cdict):
        char_uri = URIRef(MDCU[cdict['id'].lower()])
        self.triples.add((char_uri, RDF.type, MDCU['character']))
        for (key, val) in cdict.items():
            if 'publisher' == key and None != val:
                if DC_COMICS_PUB_ID == val:
                    self.triples.add((char_uri, DBP['publisher'], DBR['DC_Comics']))
                elif MARVEL_PUB_ID == val:
                    self.triples.add((char_uri, DBP['publisher'], DBR['Marvel_Comics']))
            elif 'name' == key and None != val:
                self.triples.add((char_uri, FOAF['name'], Literal(val)))
            elif 'real_name' == key and None != val:
                self.triples.add((char_uri, MDCU['real_name'], Literal(val)))
            elif 'current_alias' == key and None != val:
                self.triples.add((char_uri, MDCU['current_alias'], Literal(val)))
            elif 'alignment' == key and None != val:
                alignment_uri = URIRef(MDCU['alignment_' + compile_string_as_uri(val)])
                # add alignment class
                self.triples.add((alignment_uri, RDF.type, MDCU['alignment']))
                self.triples.add((alignment_uri, RDFS.label, Literal(val)))
                # link character to alignment
                self.triples.add((char_uri, MDCU['has_alignment'], alignment_uri))
            elif 'identity' == key and None != val:
                identity_uri = URIRef(MDCU['identity_' + compile_string_as_uri(val)])
                # add identity class
                self.triples.add((identity_uri, RDF.type, MDCU['identity']))
                self.triples.add((identity_uri, RDFS.label, Literal(val)))
                # link character to identity
                self.triples.add((char_uri, MDCU['has_identity'], identity_uri))
            elif 'race' == key and None != val:
                # TODO: is 'Human' default???
                race_uri = URIRef(MDCU['race_' + compile_string_as_uri(val)])
                # add race class
                self.triples.add((race_uri, RDF.type, DBP['species']))
                self.triples.add((race_uri, RDFS.label, Literal(val)))
                # link character to race
                self.triples.add((char_uri, MDCU['has_race'], race_uri))
            elif 'citizenship' == key and None != val:
                citizenship_uri = URIRef(MDCU['citizenship_' + compile_string_as_uri(val)])
                # add citizenship class
                self.triples.add((citizenship_uri, RDF.type, MDCU['citizenship']))
                self.triples.add((citizenship_uri, RDFS.label, Literal(val)))
                # link character to citizenship
                self.triples.add((char_uri, MDCU['has_citizenship'], citizenship_uri))
            elif 'marital_status' == key and None != val:
                self.triples.add((char_uri, MDCU['marital_status'], Literal(val)))
            elif 'gender' == key and None != val:
                self.triples.add((char_uri, FOAF['gender'], Literal(val.lower(), lang='en')))
            elif 'height' == key and None != val:
                hei_ft = val.split("'")[0].strip()
                hei_in = val.split("'")[1].split('"')[0].strip()
                hei_cm = int(int(hei_ft) * FT_TO_CM + int(hei_in) * IN_TO_CM)
                self.triples.add((char_uri, MDCU['height'], Literal(hei_cm, datatype=XSD.integer)))
            elif 'weight' == key and None != val:
                weight = val.split(' ')[0]
                self.triples.add((char_uri, MDCU['weight'], Literal(weight, datatype=XSD.integer)))
            elif 'eyes' == key and None != val:
                self.triples.add((char_uri, MDCU['eyes'], Literal(val)))
            elif 'hair' == key and None != val:
                self.triples.add((char_uri, MDCU['hair'], Literal(val)))
            elif 'aliases' == key:
                for alias in val:
                    clean_alias = re.sub('\[.*?\]', '', alias)
                    self.triples.add((char_uri, DBP['aliases'], Literal(clean_alias)))
            elif 'relatives' == key:
                for relative in val:
                    relative_uri = relative[0].split('?')[0].lower()
                    relative_relation = 'relative_' + compile_string_as_uri(relative[1])
                    if 'aka' in relative_relation:
                        continue
                    # add relative_relation as subproperty
                    self.triples.add((MDCU[relative_relation], RDFS.subPropertyOf, MDCU['relative']))
                    # link via new subproperty
                    self.triples.add((char_uri, MDCU[relative_relation], URIRef(MDCU[relative_uri])))
            elif 'affiliations' == key:
                for affiliation in val:
                    affiliation_uri = URIRef(MDCU[affiliation[0].lower()])
                    # add affiliation (team) class
                    self.triples.add((affiliation_uri, RDF.type, MDCU['team']))
                    self.triples.add((affiliation_uri, RDFS.label, Literal(affiliation[1])))
                    # link character to affiliation (team)
                    self.triples.add((char_uri, DBP['alliances'], affiliation_uri))
                    # link affiliation (team) to character
                    self.triples.add((affiliation_uri, MDCU['has_member'], char_uri))
            elif 'operation_bases' == key:
                for op_base in val:
                    op_base_uri = URIRef(MDCU[op_base[0].split('?')[0].lower()])
                    # add operation base (Place) class
                    self.triples.add((op_base_uri, RDF.type, SCHEMA['Place']))
                    self.triples.add((op_base_uri, RDFS.label, Literal(op_base[1])))
                    # link character to operation base (Place)
                    self.triples.add((char_uri, MDCU['operation_base'], op_base_uri))
            elif 'occupations' == key:
                for occupation in val:
                    occupation_uri = URIRef(MDCU['occupation_' + compile_string_as_uri(occupation)])
                    # add occupation class
                    self.triples.add((occupation_uri, RDF.type, MDCU['occupation']))
                    self.triples.add((occupation_uri, RDFS.label, Literal(occupation)))
                    # link character to occupation
                    self.triples.add((char_uri, MDCU['has_occupation'], occupation_uri))
            elif 'creators' == key:
                for creator in val:
                    creator_uri = URIRef(MDCU[creator[0]])
                    # add creator as class
                    self.triples.add((creator_uri, RDF.type, MDCU['creator']))
                    self.triples.add((creator_uri, RDFS.label, Literal(creator[1])))
                    # add creator_role as subproperty
                    self.triples.add((MDCU['role_char_creator'], RDFS.subPropertyOf, MDCU['has_creator']))
                    # link character to creator via new subproperty
                    self.triples.add((char_uri, MDCU['role_char_creator'], creator_uri))
            elif 'place_of_birth' == key and None != val[0]:
                pob_uri = URIRef(MDCU[compile_string_as_uri(val[0])])
                # add place of birth (Place) class
                self.triples.add((pob_uri, RDF.type, SCHEMA['Place']))
                self.triples.add((pob_uri, RDFS.label, Literal(val[1])))
                # link character to place
                self.triples.add((char_uri, SCHEMA['birthPlace'], pob_uri))
            elif 'first_appearance' == key and None != val[1]:
                fa_date_str = curate_comicvine_date_field(val[1])
                if None != fa_date_str:
                    self.triples.add((char_uri, MDCU['first_appearance'], Literal(fa_date_str, datatype=XSD.date)))
            elif 'trivia_facts' == key:
                for tfact in val:
                    clean_tfact = re.sub('\[.*?\]', '', tfact)
                    self.triples.add((char_uri, MDCU['trivia_fact'], Literal(clean_tfact)))
            elif 'powers' == key:
                for power in val:
                    power_uri = URIRef(MDCU['power_' + compile_string_as_uri(power)])
                    # add power class
                    self.triples.add((power_uri, RDF.type, MDCU['power']))
                    self.triples.add((power_uri, RDFS.label, Literal(power)))
                    # link character to power
                    self.triples.add((char_uri, DBP['powers'], power_uri))
            elif 'abilities' == key:
                for ability in val:
                    ability_uri = URIRef(MDCU['ability_' + compile_string_as_uri(ability)])
                    # add ability class
                    self.triples.add((ability_uri, RDF.type, MDCU['ability']))
                    self.triples.add((ability_uri, RDFS.label, Literal(ability)))
                    # link character to ability
                    self.triples.add((char_uri, MDCU['has_ability'], ability_uri))
            elif 'weaknesses' == key:
                for weakness in val:
                    weakness_uri = URIRef(MDCU['weakness_' + compile_string_as_uri(weakness)])
                    # add weakness class
                    self.triples.add((weakness_uri, RDF.type, MDCU['weakness']))
                    self.triples.add((weakness_uri, RDFS.label, Literal(weakness)))
                    # link character to weakness
                    self.triples.add((char_uri, MDCU['has_weakness'], weakness_uri))

    def add_comic_issue(self, cdict):
        cissue_uri = URIRef(MDCU['issue_' + compile_string_as_uri(cdict['id'])])
        self.triples.add((cissue_uri, RDF.type, MDCU['issue']))
        for (key, val) in cdict.items():
            if 'publisher' == key and None != val:
                if DC_COMICS_PUB_ID == val:
                    self.triples.add((cissue_uri, DBP['publisher'], DBR['DC_Comics']))
                elif MARVEL_PUB_ID == val:
                    self.triples.add((cissue_uri, DBP['publisher'], DBR['Marvel_Comics']))
            elif 'name' == key and None != val:
                self.triples.add((cissue_uri, FOAF['name'], Literal(val)))
            elif 'volume' == key and None != val:
                self.triples.add((cissue_uri, MDCU['volume'], Literal(val)))
            elif 'issue_number' == key and None != val:
                self.triples.add((cissue_uri, MDCU['issue_number'], Literal(val, datatype=XSD.integer)))
            elif 'cover_date' == key and None != val:
                 if "n/a" not in val.lower():
                    cover_date_str = curate_comicvine_date_field(val)
                    if None != cover_date_str:
                        self.triples.add((cissue_uri, MDCU['cover_date'], Literal(cover_date_str, datatype=XSD.date)))
            elif 'in_store_date' == key and None != val:
                if "n/a" not in val.lower():
                    ins_date_str = curate_comicvine_date_field(val)
                    if None != ins_date_str:
                        self.triples.add((cissue_uri, MDCU['in_store_date'], Literal(ins_date_str, datatype=XSD.date)))
            elif 'creators' == key:
                for creator in val:
                    creator_uri = URIRef(MDCU[creator[0]])
                    self.triples.add((creator_uri, RDF.type, MDCU['creator']))
                    self.triples.add((creator_uri, RDFS.label, Literal(creator[1])))
                    for crole in creator[2]:
                        creator_role = "role_" + crole.lower()
                        # add creator_role as subproperty
                        self.triples.add((MDCU[creator_role], RDFS.subPropertyOf, MDCU['has_creator']))
                        # link via new subproperty
                        self.triples.add((cissue_uri, MDCU[creator_role], creator_uri))
            elif 'characters' == key:
                for character in val:
                    self.triples.add((cissue_uri, MDCU['issue_character_appearance'], URIRef(MDCU[character[0].lower()])))
            elif 'teams' == key:
                for team in val:
                    # add team
                    team_uri = URIRef(MDCU[compile_string_as_uri(team[0])])
                    self.triples.add((team_uri, RDF.type, MDCU['team']))
                    self.triples.add((team_uri, RDFS.label, Literal(team[1])))
                    # add team as object
                    self.triples.add((cissue_uri, MDCU['issue_team_appearance'], team_uri))
            elif 'locations' == key:
                for location in val:
                    location_uri = URIRef(MDCU[location[0]])
                    # add place
                    self.triples.add((location_uri, RDF.type, SCHEMA['Place']))
                    self.triples.add((location_uri, RDFS.label, Literal(location[1])))
                    # add place as object
                    self.triples.add((cissue_uri, MDCU['location_appearance'], location_uri))
            elif 'score' == key and None != val:
                self.triples.add((cissue_uri, MDCU['rating'], Literal(val, datatype=XSD.decimal)))
            elif 'abstract' == key and None != val:
                self.triples.add((cissue_uri, DBO['abstract'], Literal(val)))

    def add_movie(self, cdict):
        cmovie_uri = URIRef(MDCU['movie_' + cdict['url'].split('?')[0].split("/")[-2].lower()])
        self.triples.add((cmovie_uri, RDF.type, MDCU['movie']))
        for (key, val) in cdict.items():
            if 'title' == key and None != val:
                self.triples.add((cmovie_uri, FOAF['name'], Literal(val)))
            elif 'rate' == key and None != val:
                self.triples.add((cmovie_uri, MDCU['rating'], Literal(val, datatype=XSD.decimal)))
            elif 'motion_pic_rate' == key and None != val:
                self.triples.add((cmovie_uri, MDCU['motion_picture_rating'], Literal(val)))
            elif 'story_line' == key and None != val:
                self.triples.add((cmovie_uri, DBO['abstract'], Literal(val)))
            elif 'genres' == key:
                for genre in val:
                    # add genre
                    genre_uri = URIRef(MDCU['genre_' + genre.lower()])
                    self.triples.add((genre_uri, RDF.type, MDCU['genre']))
                    self.triples.add((genre_uri, RDFS.label, Literal(genre)))
                    # add genre as object
                    self.triples.add((cmovie_uri, MDCU['has_genre'], genre_uri))
            elif 'key_words' == key:
                for keyword in val:
                    self.triples.add((cmovie_uri, MDCU['key_word'], Literal(compile_string_as_uri(keyword))))
            elif 'release_date' == key and None != val:
                self.triples.add((cmovie_uri, MDCU['release_date'], Literal(val.split(' ')[0], datatype=XSD.date)))
            elif 'characters' == key:
                for character in val:
                    if 'Additional Voices' in character:
                        continue
                    self.triples.add((cmovie_uri, MDCU['movie_character_appearance'], URIRef(MDCU[compile_string_as_uri(character)])))

try:
    # initialize graph
    graph = ComicsGraph()
    chars_dc_read_file = open('dc_wikia.clean.demo.jl', "r")
    counter = 0
    for line in chars_dc_read_file:
        tdi = json.loads(line)
        graph.add_character(tdi)
        counter += 1
        if counter > 1:
            break
    comicvine_read_file = open('comicvine_issues.clean.demo.jl', "r")
    for line in comicvine_read_file:
        tdi = json.loads(line)
        graph.add_comic_issue(tdi)
    imdb_read_file = open('imdb.clean.demo.jl', "r")
    for line in imdb_read_file:
        tdi = json.loads(line)
        graph.add_movie(tdi)
finally:
    chars_dc_read_file.close()
    comicvine_read_file.close()
    imdb_read_file.close()
    graph.triples.serialize("comics.demo.ttl", format="turtle")