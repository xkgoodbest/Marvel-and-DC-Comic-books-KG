'''
    Author: Basel Shbita
    Date created: 11/15/2018
    This script cleans and extracts data from dc-wikia website
'''

import string
# command-line arguments
import sys
# json ser-des utilities
import json
# beautiful soup
from bs4 import BeautifulSoup
# to maintain ordered-dictionaries
from collections import OrderedDict

# process arguments: open files to process/write
read_file = open('dc_wikia.unfiltered.jl', "r")
write_file = open('dc_wikia.clean.jl', "w")

NUM_OF_REQ_BS_IN_URL = 5
NUM_OF_REQ_QM_IN_URL = 1
DC_COMICS_PUB_ID = '_dc-comics_4010-10_'

def get_personal_attributes(raw_wiki_box):
    name = raw_wiki_box.find("h2", {"class": "pi-item pi-item-spacing pi-title"}).get_text().strip()
    real_name, current_alias, alignment, identity, \
        race, citizenship, marital_status, gender, height, weight, eyes, hair = \
        None, None, None, None, None, None, None, None, None, None, None, None
    list_of_aliases = [] # [ alias, .. ]
    list_of_relatives = [] #[ (id, name, relation) ... ]
    list_of_affiliation = [] #[ (id, name) ... ]
    list_of_op_bases = [] #[ (id, name) ... ]
    list_of_occupations = [] #[ occupation, ... ]
    list_of_creators = [] #[ (id, name) ... ]
    place_of_birth = (None, None)
    first_appr = (None, None)

    pers_attrs = raw_wiki_box.find_all("div", {"class": "pi-item pi-data pi-item-spacing pi-border-color"})
    for idx, item in enumerate(pers_attrs):
        h3_item_text = item.find("h3", {"class": "pi-data-label pi-secondary-font"}).get_text()
        div_item = item.find("div", {"class": "pi-data-value pi-font"})
        if 'Real Name' in h3_item_text:
            real_name = div_item.get_text().strip()
        elif 'Current Alias' in h3_item_text:
            current_alias = div_item.get_text().strip()
        elif 'Aliases' in h3_item_text:
            aliases = div_item.get_text().split(',')
            for alias in aliases:
                list_of_aliases.append(alias.strip())
        elif 'Relatives' in h3_item_text:
            a_tags = div_item.find_all("a")
            a_strs = str(div_item).split('<a')
            for rel_idx, relative_str in enumerate(a_strs):
                if 0 == rel_idx:
                    continue
                if '(' in relative_str:
                    rel_uri = get_clean_uri(a_tags[rel_idx - 1]['href'])
                    rel_relation = relative_str.split('(')[-1].split(')')[0].split(',')[0]
                    list_of_relatives.append((rel_uri, rel_relation))
        elif 'Affiliation' in h3_item_text:
            a_tags = div_item.find_all("a")
            for aff_a_tag in a_tags:
                aff_uri = get_clean_uri(aff_a_tag['href'])
                aff_name = aff_a_tag.get_text()
                list_of_affiliation.append((aff_uri, aff_name))
        elif 'Base Of Operations' in h3_item_text:
            a_tags = div_item.find_all("a")
            for op_a_tag in a_tags:
                op_uri = get_clean_uri(op_a_tag['href'])
                op_name = op_a_tag.get_text()
                list_of_op_bases.append((op_uri, op_name))
        elif 'Alignment' in h3_item_text:
            alignment = div_item.get_text().strip()
        elif 'Identity' in h3_item_text:
            identity = div_item.get_text().strip()
        elif 'Race' in h3_item_text:
            race = div_item.get_text().strip()
        elif 'Citizenship' in h3_item_text:
            citizenship = div_item.get_text().strip()
        elif 'Marital Status' in h3_item_text:
            marital_status = div_item.get_text().strip()
        elif 'Occupation' in h3_item_text:
            a_tags = div_item.find_all("a")
            for oc_a_tag in a_tags:
                oc_name = oc_a_tag.get_text()
                list_of_occupations.append(oc_name)
        elif 'Gender' in h3_item_text:
            gender = div_item.get_text().strip()
        elif 'Height' in h3_item_text:
            height = div_item.get_text().strip()
        elif 'Weight' in h3_item_text:
            weight = div_item.get_text().split('(')[-1].split(')')[0].strip()
        elif 'Eyes' in h3_item_text:
            eyes = div_item.get_text().strip()
        elif 'Hair' in h3_item_text:
            hair = div_item.get_text().strip()
        elif 'Place of Birth' in h3_item_text:
            place_of_birth_uri = div_item.find("a")['href']
            place_of_birth_name = div_item.get_text().strip()
            place_of_birth = (place_of_birth_uri, place_of_birth_name)
        elif 'Creators' in h3_item_text:
            a_tags = div_item.find_all("a")
            for creator_a_tag in a_tags:
                creator_uri = get_clean_uri(creator_a_tag['href'])
                creator_name = creator_a_tag.get_text()
                list_of_creators.append((creator_uri, creator_name))

    th_tf_attr = raw_wiki_box.find("table", {"class": "pi-horizontal-group"}).find_all(['th', 'td'])
    for horiz_idx, horiz_item in enumerate(th_tf_attr, start=1):
        # since we start enumerating from '1', idx will hold the index of the next-cell
        if horiz_item.name == 'th' and 'First Appearance' in horiz_item.get_text():
            if th_tf_attr[horiz_idx].name == 'td':
                access_idx = horiz_idx
            elif th_tf_attr[horiz_idx + 1].name == 'td':
                access_idx = horiz_idx + 1
            horiz_item_with_appearance_info = th_tf_attr[access_idx]
            first_appr_uri = horiz_item_with_appearance_info.find("a")['href']
            first_appr_date = horiz_item_with_appearance_info.get_text().strip().split('(')[-1].split(')')[0]
            first_appr = (first_appr_uri, first_appr_date)
                
    return name, real_name, current_alias, alignment, identity, \
        race, citizenship, marital_status, gender, height, weight, eyes, hair, \
        list_of_aliases, list_of_relatives, list_of_affiliation, \
        list_of_op_bases, list_of_occupations, list_of_creators, place_of_birth, first_appr

def get_list_of_bold_items_in_ul(ul_element):
    mylist = []
    for item in ul_element.find_all('li'):
        mylist.append(item.find('b').get_text())
    return mylist

def get_trivia_powers_abilities_weaknesses(h2_h3_uls_cntnt):
    trivia_facts = [] # [ fact, ... ]
    list_of_powers = [] # [ power, ... ]
    list_of_abilities = [] # [ ability, ... ]
    list_of_weaknesses = [] # [ weakness, ... ]
    for idx, item in enumerate(h2_h3_uls_cntnt):
        if item.name == 'h2' and 'Trivia' in item.get_text():
            for int_item in h2_h3_uls_cntnt[idx + 1].find_all('li'):
                if not "no trivia" in int_item.get_text().lower():
                    trivia_facts.append(int_item.get_text().strip())
        if item.name == 'h2' and 'Powers and Abilities' in item.get_text():
            for rem_idx, rem_itm in enumerate(h2_h3_uls_cntnt[idx:]):
                if rem_itm.name == 'h3' and 'Powers' in rem_itm.get_text():
                    list_of_powers = get_list_of_bold_items_in_ul(h2_h3_uls_cntnt[idx:][rem_idx + 1])
                if rem_itm.name == 'h3' and 'Abilities' in rem_itm.get_text():
                    list_of_abilities = get_list_of_bold_items_in_ul(h2_h3_uls_cntnt[idx:][rem_idx + 1])
                if rem_itm.name == 'h3' and 'Weaknesses' in rem_itm.get_text():
                    list_of_weaknesses = get_list_of_bold_items_in_ul(h2_h3_uls_cntnt[idx:][rem_idx + 1])
    return trivia_facts, list_of_powers, list_of_abilities, list_of_weaknesses

def get_clean_uri(dirty_string):
    return dirty_string.replace('/', '_').replace('(', '_').replace(')', '_')

try:
    # for each line in json-input file
    counter = 0
    for line_r in read_file:
        # define a temporary (output) ordered-dictionary to hold required keys
        tdo = OrderedDict()
        # load each line as a dictionary
        temp_dict_in = json.loads(line_r)
        # get url
        page_url = temp_dict_in['url']

        # if webpage is not required, skip
        num_of_bs_in_url = len(page_url.split('/'))
        num_of_qm_in_url = len(page_url.split('?'))

        if NUM_OF_REQ_BS_IN_URL != num_of_bs_in_url or \
           NUM_OF_REQ_QM_IN_URL != num_of_qm_in_url or \
           'Category:' in page_url or 'File:' in page_url: 
            continue

        tdo['id'] = get_clean_uri(page_url).split('dc.wikia.com')[1]
        
        # get html raw content from crawled data
        curr_html_doc = temp_dict_in['raw_content']
        curr_soup = BeautifulSoup(curr_html_doc, 'html.parser')
        
        # get publisher
        tdo['publisher'] = DC_COMICS_PUB_ID

        # print progress
        print("Processing[" + str(counter) + "]: " + str(tdo['id']) + " [" + str(page_url) + "]")
        counter += 1

        # find the mw-content-text
        mwcontenttext_div = curr_soup.find("div", {"id": "mw-content-text"})
        # find the wiki-details tag
        wikidet_div = mwcontenttext_div.find("aside")

        tdo['name'], tdo['real_name'], tdo['current_alias'], tdo['alignment'], tdo['identity'], \
        tdo['race'], tdo['citizenship'], tdo['marital_status'], tdo['gender'], tdo['height'], tdo['weight'], tdo['eyes'], tdo['hair'], \
        tdo['aliases'], tdo['relatives'], tdo['affiliations'], \
        tdo['operation_bases'], tdo['occupations'], tdo['creators'], \
        tdo['place_of_birth'], tdo['first_appearance'] = get_personal_attributes(wikidet_div)

        h2_within_mwcontenttext_div = mwcontenttext_div.find_all(['h2', 'h3', 'ul'])
        tdo['trivia_facts'], tdo['powers'], tdo['abilities'], \
        tdo['weaknesses'] = get_trivia_powers_abilities_weaknesses(h2_within_mwcontenttext_div)
        
        '''
        TODO:
        -----

        # get character overview/origin
        tdo['abstract'] = 

        # get character image url
        tdo['image_url']
        '''

        # provenance info
        tdo['prov_url'] = page_url
        tdo['prov_timestamp'] = temp_dict_in['timestamp_crawl']

        # serialize constructed dictionary to an output JSON-line
        # print(json.dumps(tdo, indent=2))
        temp_string = json.dumps(tdo)

        # write/append JSON-line to the output file
        write_file.write(temp_string + '\n')
        if counter > 5:
            break

        
finally:
    # safely close files
    read_file.close()
    write_file.close()
