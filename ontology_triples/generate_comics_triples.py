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
error_file_h =  open('gerrors.txt', "w")
season_to_month = {'Fall, ': 'September, ', 
                   'Winter, ': 'December, ',
                   'Spring, ': 'March, ',
                   'Summer, ': 'June, '}
bad_words_hair_eyes_cat = ['unknown', 'various', 'unrevealed', \
                           'eye', 'with', 'formerly', 'none', 'not', \
                           'variable', 'n/a', 'with', 'hair', 'varying', 'while']
valid_marital_statuses = ['single', 'married', 'widow', 'divorced', 'separated', 'engaged', 'dating']

SCHEMA = Namespace('http://schema.org/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DBP = Namespace('http://dbpedia.org/property/')
DBO = Namespace('http://dbpedia.org/ontology/')
DBR = Namespace('http://dbpedia.org/resource/')
MDCU = Namespace('http://inf558.org/comics#')

def compile_string_as_uri(ustring):
    u1string = re.sub('[^0-9a-z_]', '',
        replace_vector_of_chars_by_char(ustring.split('?')[0], ['/', ' ', '.', '-', ')', '('], '_').lower())
    return u1string

def get_first_split_by_vector_of_chars(dstring, vec_of_chars):
    for char in vec_of_chars:
        dstring = dstring.split(char)[0].strip()
    return dstring

def replace_vector_of_chars_by_char(dstring, vec_of_chars, new_char):
    for char in vec_of_chars:
        dstring = dstring.replace(char, new_char)
    return dstring

def strip_brackets_in_string(dstring):
    return re.sub('\[.*?\]', '', dstring).strip()

def curate_comicvine_date_field(string_date_field, uri):
    date_str = string_date_field
    for season, month in season_to_month.items():
        date_str = date_str.replace(season, month)
    match_cnt = 0
    for month, num in month_to_num.items():
        if num == 0:
            continue
        if month.lower() in date_str.lower():
            match_cnt += 1
    str_split_by_space = date_str.split(' ')
    if 0 == match_cnt and 1 != len(str_split_by_space):
        error_file_h.write("ERROR! should be some DATE but instead: '%s' (%s)\n" % (date_str, uri))
        return None
    for cexeption in ['1st', 'nd', 'rd', 'th']:
        if cexeption in date_str.lower():
            error_file_h.write("ERROR! should be some DATE but instead: '%s' (%s)\n" % (date_str, uri))
            return None
    date_year = '1900'
    date_month = 'January'
    date_day = 1
    if 1 == len(str_split_by_space):
        date_year = str_split_by_space[0].strip()
        if False == date_year.isdigit():
            return None
    elif 2 == len(str_split_by_space):
        date_month = str_split_by_space[0].strip()
        date_year = str_split_by_space[1].strip()
    elif 3 == len(str_split_by_space):
        date_day = int(str_split_by_space[1].split(',')[0].strip())
        date_month = str_split_by_space[0].strip()
        date_year = str_split_by_space[2].strip()
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
        char_uri = URIRef(MDCU[compile_string_as_uri(cdict['id'])])
        self.triples.add((char_uri, RDF.type, MDCU['character']))
        for (key, val) in cdict.items():
            if 'publisher' == key and None != val:
                if DC_COMICS_PUB_ID == val:
                    self.triples.add((char_uri, DBP['publisher'], DBR['DC_Comics']))
                elif MARVEL_PUB_ID == val:
                    self.triples.add((char_uri, DBP['publisher'], DBR['Marvel_Comics']))
            elif 'name' == key and None != val:
                self.triples.add((char_uri, FOAF['name'], Literal(strip_brackets_in_string(val))))
            elif 'real_name' == key and None != val:
                clean_real_name = strip_brackets_in_string(val)
                valid_real_name = True
                for cexeption in bad_words_hair_eyes_cat:
                    if cexeption in clean_real_name.split(' ')[0].lower():
                        valid_real_name = False
                        break
                if valid_real_name:
                    self.triples.add((char_uri, MDCU['real_name'], Literal(clean_real_name)))
            elif 'current_alias' == key and None != val:
                self.triples.add((char_uri, MDCU['current_alias'], Literal(strip_brackets_in_string(val))))
            elif 'alignment' == key and None != val:
                alignment_uri = URIRef(MDCU['alignment_' + compile_string_as_uri(val)])
                # add alignment class
                self.triples.add((alignment_uri, RDF.type, MDCU['alignment']))
                self.triples.add((alignment_uri, RDFS.label, Literal(val)))
                # link character to alignment
                self.triples.add((char_uri, MDCU['has_alignment'], alignment_uri))
            elif 'identity' == key and None != val:
                clean_identity = strip_brackets_in_string(val.split('(')[0])
                identity_uri = URIRef(MDCU['identity_' + compile_string_as_uri(clean_identity).split('__')[0]])
                # add identity class
                self.triples.add((identity_uri, RDF.type, MDCU['identity']))
                self.triples.add((identity_uri, RDFS.label, Literal(clean_identity)))
                # link character to identity
                self.triples.add((char_uri, MDCU['has_identity'], identity_uri))
            elif 'race' == key and None != val:
                clean_race = strip_brackets_in_string(val)
                race_uri = URIRef(MDCU['race_' + compile_string_as_uri(clean_race)])
                # add race class
                self.triples.add((race_uri, RDF.type, MDCU['race']))
                self.triples.add((race_uri, RDFS.label, Literal(clean_race)))
                # link character to race
                self.triples.add((char_uri, DBP['species'], race_uri))
            elif 'citizenship' == key and None != val:
                clean_cit = strip_brackets_in_string(val)
                citizenship_uri = URIRef(MDCU['citizenship_' + compile_string_as_uri(clean_cit)])
                # add citizenship class
                self.triples.add((citizenship_uri, RDF.type, MDCU['citizenship']))
                self.triples.add((citizenship_uri, RDFS.label, Literal(clean_cit)))
                # link character to citizenship
                self.triples.add((char_uri, MDCU['has_citizenship'], citizenship_uri))
            elif 'marital_status' == key and None != val:
                clean_marital_status = get_first_split_by_vector_of_chars(strip_brackets_in_string(val).lower(), [' ', ';', ','])
                for valid_mar_sts in valid_marital_statuses:
                    if clean_marital_status in valid_mar_sts:
                        self.triples.add((char_uri, MDCU['marital_status'], Literal(valid_mar_sts)))
            elif 'gender' == key and None != val:
                clean_gender = get_first_split_by_vector_of_chars(strip_brackets_in_string(val).lower(), ['(', '/', ';', ',', ' ', 'formerly'])
                self.triples.add((char_uri, FOAF['gender'], Literal(clean_gender, lang='en')))
            elif 'height' == key and None != val:
                hei_str = get_first_split_by_vector_of_chars(val, ['(', ';'])
                if (not "'" in hei_str) or (not '"' in hei_str):
                    continue
                else:
                    valid_hei = True
                    for cexeption in ['(', 'unknown', 'variable', 'unmeasured', 'physical']:
                        if cexeption in hei_str.lower():
                            valid_hei = False
                            break
                    if valid_hei:
                        hei_ft = hei_str.split("'")[0].strip()
                        hei_in = get_first_split_by_vector_of_chars(hei_str, ["'", '"'])
                        hei_cm = int(int(hei_ft) * FT_TO_CM + int(hei_in) * IN_TO_CM)
                        self.triples.add((char_uri, MDCU['height'], Literal(hei_cm, datatype=XSD.integer)))
                    else: 
                        error_file_h.write("ERROR! should be some HEIGHT but instead: '%s' (%s)\n" % (hei_str, char_uri))
            elif 'weight' == key and None != val:
                val_split_list = val.split(' ')
                if len(val_split_list) > 1 and 'kg' in val.split(' ')[1]:
                    weight = get_first_split_by_vector_of_chars(val, [' ', '-'])
                    self.triples.add((char_uri, MDCU['weight'], Literal(weight, datatype=XSD.integer)))
            elif 'eyes' == key and None != val:
                clean_eyes = get_first_split_by_vector_of_chars(strip_brackets_in_string(val.lower()), [' ', ';', ',', '(', '.'])
                if len(clean_eyes) < 3:
                    continue
                else:
                    valid_eyes = True
                    for cexeption in bad_words_hair_eyes_cat:
                        if cexeption == clean_eyes:
                            valid_eyes = False
                            break
                    if valid_eyes:
                        self.triples.add((char_uri, MDCU['eyes'], Literal(clean_eyes)))
            elif 'hair' == key and None != val:
                clean_hair = get_first_split_by_vector_of_chars(strip_brackets_in_string(val.lower()), [' ', ';', ',', '(', '.'])
                if len(clean_hair) < 3:
                    continue
                else:
                    valid_hair = True
                    for cexeption in bad_words_hair_eyes_cat:
                        if cexeption == clean_hair:
                            valid_hair = False
                            break
                    if valid_hair:
                        self.triples.add((char_uri, MDCU['hair'], Literal(clean_hair)))
            elif 'aliases' == key:
                for alias in val:
                    clean_alias = strip_brackets_in_string(alias)
                    if '' == clean_alias or "None" == clean_alias:
                        continue
                    self.triples.add((char_uri, DBP['aliases'], Literal(clean_alias)))
            elif 'relatives' == key:
                for relative in val:
                    if 'aka' in relative[1] or 'see' in relative[1] or \
                       'possible' in relative[1] or '&' in relative[1] or '?' in relative[1]:
                        continue
                    relative_uri = URIRef(MDCU[compile_string_as_uri(relative[0])])
                    relative_relation_uri = URIRef(MDCU['relative_' + \
                        compile_string_as_uri(get_first_split_by_vector_of_chars(relative[1], ['<', ';', ':']).replace("'",''))])
                    # add relative_relation as subproperty
                    self.triples.add((relative_relation_uri, RDFS.subPropertyOf, MDCU['relative']))
                    # link via new subproperty
                    self.triples.add((char_uri, relative_relation_uri, relative_uri))
            elif 'affiliations' == key:
                # TODO: fix the #cite_note problem!!
                for affiliation in val:
                    if '[' in affiliation[1]:
                        error_file_h.write("ERROR! '[' in AFFLIATION: '%s' (%s)\n" % (affiliation, char_uri))
                    affiliation_uri = URIRef(MDCU[compile_string_as_uri(affiliation[0].replace(':', '_'))])
                    # add affiliation (team) class
                    self.triples.add((affiliation_uri, RDF.type, MDCU['team']))
                    self.triples.add((affiliation_uri, RDFS.label, Literal(affiliation[1])))
                    # link character to affiliation (team)
                    self.triples.add((char_uri, DBP['alliances'], affiliation_uri))
                    # link affiliation (team) to character
                    self.triples.add((affiliation_uri, MDCU['has_member'], char_uri))
            elif 'operation_bases' == key:
                for op_base in val:
                    op_base_uri = URIRef(MDCU[compile_string_as_uri(op_base[0])])
                    # add operation base (Place) class
                    self.triples.add((op_base_uri, RDF.type, SCHEMA['Place']))
                    self.triples.add((op_base_uri, RDFS.label, Literal(strip_brackets_in_string(op_base[1]))))
                    # link character to operation base (Place)
                    self.triples.add((char_uri, MDCU['operation_base'], op_base_uri))
            elif 'occupations' == key:
                for occupation in val:
                    clean_occu_str = replace_vector_of_chars_by_char(strip_brackets_in_string(occupation).split(';')[0],
                        ['{', '}', '#', '|'], '')
                    occupation_uri = URIRef(MDCU['occupation_' + compile_string_as_uri(clean_occu_str)])
                    # add occupation class
                    self.triples.add((occupation_uri, RDF.type, MDCU['occupation']))
                    self.triples.add((occupation_uri, RDFS.label, Literal(clean_occu_str)))
                    # link character to occupation
                    self.triples.add((char_uri, MDCU['has_occupation'], occupation_uri))
            elif 'creators' == key:
                for creator in val:
                    creator_uri = URIRef(MDCU[compile_string_as_uri(creator[0])])
                    # add creator as class
                    self.triples.add((creator_uri, RDF.type, MDCU['creator']))
                    self.triples.add((creator_uri, RDFS.label, Literal(creator[1])))
                    # add creator_role as subproperty
                    self.triples.add((MDCU['role_char_creator'], RDFS.subPropertyOf, MDCU['has_creator']))
                    # link character to creator via new subproperty
                    self.triples.add((char_uri, MDCU['role_char_creator'], creator_uri))
            elif 'place_of_birth' == key and None != val[0]:
                clean_pob = strip_brackets_in_string(val[1])
                pob_uri = URIRef(MDCU[compile_string_as_uri(val[0])])
                # add place of birth (Place) class
                self.triples.add((pob_uri, RDF.type, SCHEMA['Place']))
                self.triples.add((pob_uri, RDFS.label, Literal(clean_pob)))
                # link character to place
                self.triples.add((char_uri, SCHEMA['birthPlace'], pob_uri))
            elif 'first_appearance' == key and None != val[1]:
                fa_date_str = curate_comicvine_date_field(val[1], char_uri)
                if None != fa_date_str:
                    self.triples.add((char_uri, MDCU['first_appearance'], Literal(fa_date_str, datatype=XSD.date)))
            elif 'trivia_facts' == key:
                for tfact in val:
                    clean_tfact = strip_brackets_in_string(tfact)
                    self.triples.add((char_uri, MDCU['trivia_fact'], Literal(clean_tfact)))
            elif 'powers' == key:
                for power in val:
                    clean_power = strip_brackets_in_string(power.replace(':', ''))
                    power_uri = URIRef(MDCU['power_' + compile_string_as_uri(clean_power)])
                    # add power class
                    self.triples.add((power_uri, RDF.type, MDCU['power']))
                    self.triples.add((power_uri, RDFS.label, Literal(clean_power)))
                    # link character to power
                    self.triples.add((char_uri, DBP['powers'], power_uri))
            elif 'abilities' == key:
                for ability in val:
                    clean_ability = strip_brackets_in_string(ability.replace(':', ''))
                    ability_uri = URIRef(MDCU['ability_' + compile_string_as_uri(clean_ability)])
                    # add ability class
                    self.triples.add((ability_uri, RDF.type, MDCU['ability']))
                    self.triples.add((ability_uri, RDFS.label, Literal(clean_ability)))
                    # link character to ability
                    self.triples.add((char_uri, MDCU['has_ability'], ability_uri))
            elif 'weaknesses' == key:
                for weakness in val:
                    clean_weakness = strip_brackets_in_string(weakness.replace(':', ''))
                    weakness_uri = URIRef(MDCU['weakness_' + compile_string_as_uri(clean_weakness)])
                    # add weakness class
                    self.triples.add((weakness_uri, RDF.type, MDCU['weakness']))
                    self.triples.add((weakness_uri, RDFS.label, Literal(clean_weakness)))
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
                valid_issue_n = True
                for cexeption in ['AU', '½']:
                    if cexeption in val:
                        valid_issue_n = False
                        break
                if valid_issue_n:
                    self.triples.add((cissue_uri, MDCU['issue_number'], Literal(val, datatype=XSD.decimal)))
            elif 'cover_date' == key and None != val:
                 if "n/a" not in val.lower():
                    cover_date_str = curate_comicvine_date_field(val, cissue_uri)
                    if None != cover_date_str:
                        self.triples.add((cissue_uri, MDCU['cover_date'], Literal(cover_date_str, datatype=XSD.date)))
            elif 'in_store_date' == key and None != val:
                if "n/a" not in val.lower():
                    ins_date_str = curate_comicvine_date_field(val, cissue_uri)
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
                    char_uri = URIRef(MDCU[character[0].lower()])
                    self.triples.add((cissue_uri, MDCU['issue_character_appearance'], char_uri))
                    # link character to issue
                    self.triples.add((char_uri, MDCU['issue_appearance'], cissue_uri))
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
                    self.triples.add((location_uri, RDFS.label, Literal(strip_brackets_in_string(location[1]))))
                    # add place as object
                    self.triples.add((cissue_uri, MDCU['location_appearance'], location_uri))
            elif 'score' == key and None != val:
                self.triples.add((cissue_uri, MDCU['rating'], Literal(val, datatype=XSD.decimal)))
            elif 'abstract' == key and None != val:
                self.triples.add((cissue_uri, DBO['abstract'], Literal(val)))

    def add_movie(self, cdict):
        cmovie_uri = URIRef(MDCU['movie_' + compile_string_as_uri(cdict['url'].split('?')[0].split("/")[-2].lower())])
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
                    genre_uri = URIRef(MDCU['genre_' + compile_string_as_uri(genre.lower())])
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
                    char_uri = URIRef(MDCU[compile_string_as_uri(character)])
                    self.triples.add((cmovie_uri, MDCU['movie_character_appearance'], char_uri))
                    # link character to movie
                    self.triples.add((char_uri, MDCU['movie_appearance'], cmovie_uri))

try:
    # initialize graph
    graph = ComicsGraph()
    # generate dc-wikia characters triples
    dc_read_file = open('dc_wikia.clean.jl', "r")
    counter = 0
    for line in dc_read_file:
        tdi = json.loads(line)
        graph.add_character(tdi)
        counter += 1
    # generate marvel-wikia characters triples
    print('Finished generating triples for characters (DC-wikia): ' + str(counter))
    marvel_read_file = open('marvel_wikia.clean.jl', "r")
    counter = 0
    for line in marvel_read_file:
        tdi = json.loads(line)
        graph.add_character(tdi)
        counter += 1
    print('Finished generating triples for characters (Marvel-wikia): ' + str(counter))
    # generate comicvine issues triples
    comicvine_read_file = open('comicvine_issues.clean.jl', "r")
    counter = 0
    for line in comicvine_read_file:
        tdi = json.loads(line)
        graph.add_comic_issue(tdi)
        counter += 1
    print('Finished generating triples for issues (Comicvine): ' + str(counter))
    # generate imdb movies triples
    imdb_read_file = open('imdb.clean.jl', "r")
    counter = 0
    for line in imdb_read_file:
        tdi = json.loads(line)
        graph.add_movie(tdi)
        counter += 1
    print('Finished generating triples for movies (IMDB): ' + str(counter))
finally:
    dc_read_file.close()
    marvel_read_file.close()
    comicvine_read_file.close()
    imdb_read_file.close()
    error_file_h.close()
    print('Generating TTL file...')
    graph.triples.serialize("mdc_comics.ttl", format="turtle")