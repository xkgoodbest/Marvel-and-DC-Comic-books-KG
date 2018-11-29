'''
    Author: Basel Shbita
    Date created: 11/28/2018
'''

# Record Linkage ToolKit
import rltk
# to maintain ordered-dictionaries
from collections import OrderedDict
# json utilities
import json
# regular expression
import re

bad_words_hair_eyes_cat = ['unknown', 'various', 'unrevealed', \
                           'eye', 'with', 'formerly', 'none', 'not', \
                           'variable', 'n/a', 'with', 'hair', 'varying', 'while']

DC_COMICS_PUB_ID = '_dc-comics_4010-10_'
MARVEL_PUB_ID = '_marvel_4010-31_'

tokenizer = rltk.CrfTokenizer()

'''
MOVIE_CHARS_DICT --> WIKIA_CHARS_DICT
ISSUE_CHARS_DICT --> WIKIA_CHARS_DICT
'''
MOVIE_CHARS_DICT = dict()
ISSUE_CHARS_DICT = dict()
WIKIA_CHARS_DICT = dict()

SIM_CHARS__MOVIE_TO_WIKIA = dict()
SIM_CHARS__ISSUE_TO_WIKIA = dict()

'''
ISSUE_TEAMS_DICT --> WIKIA_TEAMS_DICT
'''
ISSUE_TEAMS_DICT = dict()
WIKIA_TEAMS_DICT = dict()
'''
ISSUE_LOCATIONS_DICT --> WIKIA_LOCATIONS_DICT
'''
ISSUE_LOCATIONS_DICT = dict()
WIKIA_LOCATIONS_DICT = dict()

####################################### EXTRACTION TO JSON #######################################

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

def add_character(cdict):
    char_uri = "mdcu:" + compile_string_as_uri(cdict['id'])
    publisher = None
    name = None
    real_name = None
    affliations = []
    operation_bases = []

    for (key, val) in cdict.items():
        if 'publisher' == key and None != val:
            if DC_COMICS_PUB_ID == val:
                publisher = "dbr:DC_Comics"
            elif MARVEL_PUB_ID == val:
                publisher = "dbr:Marvel_Comics"
        elif 'name' == key and None != val:
            name = strip_brackets_in_string(val)
        elif 'real_name' == key and None != val:
            clean_real_name = strip_brackets_in_string(val)
            valid_real_name = True
            for cexeption in bad_words_hair_eyes_cat:
                if cexeption in clean_real_name.split(' ')[0].lower():
                    valid_real_name = False
                    break
            if valid_real_name:
                real_name = clean_real_name
        elif 'affiliations' == key:
            for affiliation in val:
                if '[' in affiliation[1]:
                    continue
                affiliation_uri = "mdcu:" + compile_string_as_uri(affiliation[0].replace(':', '_'))
                affliations.append((affiliation_uri, affiliation[1]))
        elif 'operation_bases' == key:
            for op_base in val:
                op_base_uri = "mdcu:" + compile_string_as_uri(op_base[0])
                operation_bases.append((op_base_uri, strip_brackets_in_string(op_base[1])))
    
    WIKIA_CHARS_DICT[char_uri] = {'publisher': publisher, \
                                  'name': name, \
                                  'real_name': real_name }
    for affliation in affliations:
        WIKIA_TEAMS_DICT[affliation[0]] = {'name': affliation[1], \
                                           'publisher': publisher}
    for location in operation_bases:
        WIKIA_LOCATIONS_DICT[location[0]] = {'name': location[1]}

def add_comic_issue(cdict):
    publisher = None
    characters = []
    teams = []
    locations = []

    for (key, val) in cdict.items():
        if 'publisher' == key and None != val:
            if DC_COMICS_PUB_ID == val[0]:
                publisher = "dbr:DC_Comics"
            elif MARVEL_PUB_ID == val[0]:
                publisher = "dbr:Marvel_Comics"
        elif 'characters' == key:
            for character in val:
                char_uri = "mdcu:" + character[0].lower()
                characters.append(char_uri)
        elif 'teams' == key:
            for team in val:
                team_uri = "mdcu:" + compile_string_as_uri(team[0])
                teams.append((team_uri, team[1]))
        elif 'locations' == key:
            for location in val:
                location_uri = "mdcu:" + location[0]
                locations.append((location_uri, location[1]))

    for character in characters:
        ISSUE_CHARS_DICT[character] = {'publisher': publisher}
    for team in teams:
        ISSUE_TEAMS_DICT[team[0]] = {'name': team[1], \
                                     'publisher': publisher}
    for location in locations:
        ISSUE_LOCATIONS_DICT[location[0]] = {'name': location[1]}

def add_movie(cdict):
    key_words = []
    characters = []
    for (key, val) in cdict.items():
        if 'key_words' == key:
            for keyword in val:
                key_words.append(compile_string_as_uri(keyword))
        elif 'characters' == key:
            for character in val:
                if 'Additional Voices' in character:
                    continue
                char_uri = "mdcu:" + compile_string_as_uri(character)
                characters.append(char_uri)

    for character in characters:
        publisher = None
        for key_word in key_words:
            if 'marvel' in key_word:
                publisher = "dbr:Marvel_Comics"
            elif 'dc_comics' in key_word:
                publisher = "dbr:DC_Comics"
        if None != publisher:
            MOVIE_CHARS_DICT[character] = {'publisher': publisher}    

def generate_dicts():
    dc_read_file = open('dc_wikia.clean.jl', "r")
    marvel_read_file = open('marvel_wikia.clean.jl', "r")
    comicvine_read_file = open('comicvine_issues.clean.jl', "r")
    imdb_read_file = open('imdb.clean.jl', "r")
    # generate dc-wikia characters triples
    counter = 0
    for line in dc_read_file:
        tdi = json.loads(line)
        add_character(tdi)
        counter += 1
    # generate marvel-wikia characters triples
    print('Finished generating characters (DC-wikia): ' + str(counter))
    counter = 0
    for line in marvel_read_file:
        tdi = json.loads(line)
        add_character(tdi)
        counter += 1
    print('Finished generating characters (Marvel-wikia): ' + str(counter))
    # generate comicvine issues triples
    counter = 0
    for line in comicvine_read_file:
        tdi = json.loads(line)
        add_comic_issue(tdi)
        counter += 1
    print('Finished generating issues (Comicvine): ' + str(counter))
    # generate imdb movies triples
    counter = 0
    for line in imdb_read_file:
        tdi = json.loads(line)
        add_movie(tdi)
        counter += 1
    print('Finished generating movies (IMDB): ' + str(counter))
    dc_read_file.close()
    marvel_read_file.close()
    comicvine_read_file.close()
    imdb_read_file.close()
    with open('MOVIE_CHARS_DICT.json', 'w') as outfile:
        print(len(MOVIE_CHARS_DICT))
        json.dump(MOVIE_CHARS_DICT, outfile, indent=2)
    with open('ISSUE_CHARS_DICT.json', 'w') as outfile:
        print(len(ISSUE_CHARS_DICT))
        json.dump(ISSUE_CHARS_DICT, outfile, indent=2)
    with open('WIKIA_CHARS_DICT.json', 'w') as outfile:
        print(len(WIKIA_CHARS_DICT))
        json.dump(WIKIA_CHARS_DICT, outfile, indent=2)
    with open('ISSUE_TEAMS_DICT.json', 'w') as outfile:
        print(len(ISSUE_TEAMS_DICT))
        json.dump(ISSUE_TEAMS_DICT, outfile, indent=2)
    with open('WIKIA_TEAMS_DICT.json', 'w') as outfile:
        print(len(WIKIA_TEAMS_DICT))
        json.dump(WIKIA_TEAMS_DICT, outfile, indent=2)
    with open('ISSUE_LOCATIONS_DICT.json', 'w') as outfile:
        print(len(ISSUE_LOCATIONS_DICT))
        json.dump(ISSUE_LOCATIONS_DICT, outfile, indent=2)
    with open('WIKIA_LOCATIONS_DICT.json', 'w') as outfile:
        print(len(WIKIA_LOCATIONS_DICT))
        json.dump(WIKIA_LOCATIONS_DICT, outfile, indent=2)

####################################### JSON --> JL #######################################

def generate_jl_file(dict_name):
    input_dict = json.load(open(dict_name + '.json', "r"))
    o_file_handle = open(dict_name + '.jl', "w")
    for key, items in input_dict.items():
        temp_dict_out = OrderedDict()
        temp_dict_out['id'] = key
        for (item_k, item_v) in items.items():
            temp_dict_out[item_k] = item_v
        # serialize constructed dictionary to an output JSON-line
        temp_string = json.dumps(temp_dict_out)
        o_file_handle.write(temp_string + '\n')
    return

def open_dicts_generate_jls():
    MOVIE_CHARS_DICT = json.load(open('MOVIE_CHARS_DICT.json', "r"))
    ISSUE_CHARS_DICT = json.load(open('ISSUE_CHARS_DICT.json', "r"))
    WIKIA_CHARS_DICT = json.load(open('WIKIA_CHARS_DICT.json', "r"))
    print('MOVIE_CHARS_DICT [%d] --> WIKIA_CHARS_DICT [%d]' % (len(MOVIE_CHARS_DICT), len(WIKIA_CHARS_DICT)))
    print('ISSUE_CHARS_DICT [%d] --> WIKIA_CHARS_DICT [%d]' % (len(ISSUE_CHARS_DICT), len(WIKIA_CHARS_DICT)))
    generate_jl_file('MOVIE_CHARS_DICT')
    generate_jl_file('ISSUE_CHARS_DICT')
    generate_jl_file('WIKIA_CHARS_DICT')

    ISSUE_TEAMS_DICT = json.load(open('ISSUE_TEAMS_DICT.json', "r"))
    WIKIA_TEAMS_DICT = json.load(open('WIKIA_TEAMS_DICT.json', "r"))
    print('ISSUE_TEAMS_DICT [%d] --> WIKIA_TEAMS_DICT [%d]' % (len(ISSUE_TEAMS_DICT), len(WIKIA_TEAMS_DICT)))
    generate_jl_file('ISSUE_TEAMS_DICT')
    generate_jl_file('WIKIA_TEAMS_DICT')

    ISSUE_LOCATIONS_DICT = json.load(open('ISSUE_LOCATIONS_DICT.json', "r"))
    WIKIA_LOCATIONS_DICT = json.load(open('WIKIA_LOCATIONS_DICT.json', "r"))
    print('ISSUE_LOCATIONS_DICT [%d] --> WIKIA_LOCATIONS_DICT [%d]' % (len(ISSUE_LOCATIONS_DICT), len(WIKIA_LOCATIONS_DICT)))
    generate_jl_file('ISSUE_LOCATIONS_DICT')
    generate_jl_file('WIKIA_LOCATIONS_DICT')

####################################### RLTK COMPONENTS CONSTRUCTION #######################################

# general tokenize function used by both RLTK records
def tokenize(s):
    tokens = tokenizer.tokenize(s)
    return [w.lower() for w in tokens if w.isalpha()]

class MovieCharRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''
    @rltk.cached_property
    def id(self):
        return self.raw_object.get('id', '')
    @rltk.cached_property
    def publisher(self):
        return self.raw_object.get('publisher', '')
    @rltk.cached_property
    def full_name_string(self):
        return self.raw_object.get('id', '').split('mdcu:')[1].replace('_', ' ')
    @rltk.cached_property
    def name_tokens(self):
        tokens = tokenize(self.full_name_string)
        return set(tokens)

class IssueCharRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''
    @rltk.cached_property
    def id(self):
        return self.raw_object.get('id', '')
    @rltk.cached_property
    def publisher(self):
        return self.raw_object.get('publisher', '')
    @rltk.cached_property
    def full_name_string(self):
        return self.raw_object.get('id', '').split('mdcu:')[1].split('_4005')[0].replace('_', ' ').replace('-', ' ')
    @rltk.cached_property
    def name_tokens(self):
        tokens = tokenize(self.full_name_string)
        return set(tokens)

class WikiaCharRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''
    @rltk.cached_property
    def id(self):
        return self.raw_object.get('id', '')
    @rltk.cached_property
    def publisher(self):
        return self.raw_object.get('publisher', '')
    @rltk.cached_property
    def full_name_string(self):
        return self.raw_object.get('name', '')
    @rltk.cached_property
    def full_real_name_string(self):
        real_name = self.raw_object.get('real_name', '')
        if None != real_name:
            real_name = real_name.replace(';', ' ')
            real_name = re.sub('\(.*?\)', '', real_name).strip()
        return real_name
    @rltk.cached_property
    def name_tokens(self):
        tokens = tokenize(str(self.full_name_string) + ' ' + str(self.full_real_name_string))
        return set(tokens)

####################################### FIELD SIMILARITY AND ENTITY LINKING #######################################

# name string similarity score
def chars_movie_or_issue_to_wikia_similarity(r_movie_or_issue_char, r_wikia_char):    
    full_name_m = r_movie_or_issue_char.full_name_string.lower()
    full_name_w = r_wikia_char.full_name_string.lower()
    
    publishers_match = (r_movie_or_issue_char.publisher == r_wikia_char.publisher)

    # full name score
    if full_name_m == full_name_w and publishers_match:
        return True, 1
    # Jaccard name score for whole set of name tokens (dirty)
    jaccard_name_score = rltk.jaccard_index_similarity(r_movie_or_issue_char.name_tokens, r_wikia_char.name_tokens)
    # Jaro Winkerler name score for re-assembeled full name (clean)
    jw_name_score = rltk.jaro_winkler_similarity(full_name_m, full_name_w)
    total = jaccard_name_score * 0.65 + jw_name_score * 0.35

    if publishers_match:
        return total > 0.7, total
    else:
        return False, total/3

def find_chars_movie_or_issue_to_wikia_matching_record(r_movie_or_issue_char, ds_wikia_char):
    best_match_confidence = 0
    best_match_id = None
    for r_wikia_char in ds_wikia_char:
        # get result and confidence
        result, confidence = chars_movie_or_issue_to_wikia_similarity(r_movie_or_issue_char, r_wikia_char)
        if True == result and confidence > best_match_confidence:
            best_match_id = r_wikia_char.id
            best_match_confidence = confidence
    # return result-uri and confidence of the result
    return best_match_id, best_match_confidence

####################################### RUN THIS SHIT #######################################

def entity_links_stage_1():
    # load Datasets
    ds_movie_char = rltk.Dataset(reader=rltk.JsonLinesReader('MOVIE_CHARS_DICT.jl'), record_class=MovieCharRecord, adapter=rltk.MemoryAdapter())
    ds_wikia_char = rltk.Dataset(reader=rltk.JsonLinesReader('WIKIA_CHARS_DICT.jl'), record_class=WikiaCharRecord, adapter=rltk.MemoryAdapter())
    # print some entries
    print(ds_movie_char.generate_dataframe().head(5))
    print(ds_wikia_char.generate_dataframe().head(5))
    tot_counter = 0
    for item in ds_movie_char:
        tot_counter += 1
        res_id, res_conf = find_chars_movie_or_issue_to_wikia_matching_record(item, ds_wikia_char)
        if res_id != None:
            print('[%003d]: [%s] ---%03.02f%%--- [%s]' % (tot_counter, item.id, res_conf*100, res_id))
            SIM_CHARS__MOVIE_TO_WIKIA[item.id] = (res_id, res_conf)
    with open('SIM_CHARS__MOVIE_TO_WIKIA.json', 'w') as outfile:
        print('SIM_CHARS__MOVIE_TO_WIKIA: ' + str(len(SIM_CHARS__MOVIE_TO_WIKIA)))
        json.dump(SIM_CHARS__MOVIE_TO_WIKIA, outfile, indent=2)

def entity_links_stage_2():
    # load Datasets
    ds_issue_char = rltk.Dataset(reader=rltk.JsonLinesReader('ISSUE_CHARS_DICT.jl'), record_class=IssueCharRecord, adapter=rltk.MemoryAdapter())
    ds_wikia_char = rltk.Dataset(reader=rltk.JsonLinesReader('WIKIA_CHARS_DICT.jl'), record_class=WikiaCharRecord, adapter=rltk.MemoryAdapter())
    # print some entries
    print(ds_issue_char.generate_dataframe().head(5))
    print(ds_wikia_char.generate_dataframe().head(5))
    tot_counter = 0
    for item in ds_issue_char:
        tot_counter += 1
        res_id, res_conf = find_chars_movie_or_issue_to_wikia_matching_record(item, ds_wikia_char)
        if res_id != None:
            print('[%003d]: [%s] ---%03.02f%%--- [%s]' % (tot_counter, item.id, res_conf*100, res_id))
            SIM_CHARS__ISSUE_TO_WIKIA[item.id] = (res_id, res_conf)
    with open('SIM_CHARS__ISSUE_TO_WIKIA.json', 'w') as outfile:
        print('SIM_CHARS__ISSUE_TO_WIKIA: ' + str(len(SIM_CHARS__ISSUE_TO_WIKIA)))
        json.dump(SIM_CHARS__ISSUE_TO_WIKIA, outfile, indent=2)

try:
    # generate_dicts()
    # open_dicts_generate_jls()
    # entity_links_stage_1()
    entity_links_stage_2()
finally:
    print('Done')