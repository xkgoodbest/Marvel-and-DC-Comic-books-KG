'''
    Author: Basel Shbita
    Date created: 11/15/2018
    This script cleans and extracts data from comicvine website
'''

# command-line arguments
import sys
# json ser-des utilities
import json
# beautiful soup
from bs4 import BeautifulSoup
# to maintain ordered-dictionaries
from collections import OrderedDict

# process arguments: open files to process/write
read_file = open('comicvine_issues__2018-11-05.filtered.jl', "r")
write_file = open('comicvine_issues.clean.jl', "w")

NUM_OF_REQ_BS_IN_URL = 6
INDEX_OF_ID_IN_URL = 4
INDEX_OF_WIKI_DT = 1
INDEX_OF_CREATORS_CHARS_TEAMS_LOCATIONS_DT = 0
PUBLISHER_IDENTIFIER = '4010'
DC_COMICS_PUB_ID = '_dc-comics_4010-10_'
MARVEL_PUB_ID = '_marvel_4010-31_'

def get_abstract(raw_soup):
    return raw_soup.find("div", {"class": "wiki-item-display js-toc-content"}).get_text().strip()

def get_publisher(raw_soup):
    publisher = None # (id, name)
    subtitle_div = raw_soup.find("p", {"class": "wiki-descriptor"})
    for obj in subtitle_div.findAll("a"):
        if PUBLISHER_IDENTIFIER in obj['href']:
            publisher = (obj['href'].replace('/', '_'), obj.get_text().strip())
    return publisher

def get_issue_score(raw_soup):
    issue_score = None
    review_div = raw_soup.find("dl", {"class": "editorial user-reviews"})
    if len(review_div) > 0:
        score_div = review_div.findAll("span", {"class": "average-score"})
        if len(score_div) > 0:
            issue_score = float(score_div[0].get_text().strip().split(' ')[0])
    return issue_score

def get_issue_info_from_wiki_details_div(th_tr_attr):
    # define default values in-case they don't exist
    name = None
    volume = None
    issue_number = None
    cover_date = None
    in_store_date = None
    # iterate over the attributes (with index counter)
    for idx, item in enumerate(th_tr_attr):
        if item.name == 'tr' and 'Name' in item.get_text():
            name = item.find("div", {"data-field": "name"}).get_text().strip()
        if item.name == 'tr' and 'Volume' in item.get_text():
            volume = item.find("div", {"class": "bar wiki-item-display"}).get_text().strip()
        if item.name == 'tr' and 'Issue Number' in item.get_text():
            issue_number = item.find("div", {"data-field": "issueNumber"}).get_text().strip()
        if item.name == 'tr' and 'Cover Date' in item.get_text():
            cover_date = item.find("div", {"data-field": "cover_date"}).get_text().strip()
        if item.name == 'tr' and 'In Store Date' in item.get_text():
            in_store_date = item.find("div", {"data-field": "storeDate"}).get_text().strip()
    return name, volume, issue_number, cover_date, in_store_date

def get_creators_chars_teams_locations_from_div(list_of_objs):
    # define default values in-case they don't exist
    list_of_creators = [] #[ (id, name, [role1, .. ]) ... ]
    list_of_chars = [] #[ (id, name) ... ]
    list_of_teams = [] #[ (id, name) ... ]
    list_of_locations = [] #[ (id, name) ... ]
    # iterate over the attributes (with index counter)
    for idx, item in enumerate(list_of_objs):
        h3_tag = item.find(['h3'])
        # Creators
        if len(h3_tag) == 1 and 'Creators' in h3_tag:
            lst = item.findAll(['li'])
            for creator in lst:
                creator_id = creator.find("a")['href'].replace('/', '_')
                creator_name = creator.find("a").get_text().strip()
                creator_roles_list = []
                creator_roles = creator.find("span", {"class": "credits-role"}).get_text()
                for role in creator_roles.split(','):
                    creator_roles_list.append(role.strip())
                list_of_creators.append((creator_id, creator_name, creator_roles_list))
        # Characters
        if len(h3_tag) == 1 and 'Characters' in h3_tag:
            lst = item.findAll(['li'])
            for char in lst:
                char_id = char.find("a")['href'].replace('/', '_')
                char_name = char.find("a").get_text().strip()
                list_of_chars.append((char_id, char_name))
        # Teams
        if len(h3_tag) == 1 and 'Teams' in h3_tag:
            lst = item.findAll(['li'])
            for team in lst:
                team_id = team.find("a")['href'].replace('/', '_')
                team_name = team.find("a").get_text().strip()
                list_of_teams.append((team_id, team_name))
        # Locations
        if len(h3_tag) == 1 and 'Locations' in h3_tag:
            lst = item.findAll(['li'])
            for loc in lst:
                loc_id = loc.find("a")['href'].replace('/', '_')
                loc_name = loc.find("a").get_text().strip()
                list_of_locations.append((loc_id, loc_name))
    return list_of_creators, list_of_chars, list_of_teams, list_of_locations

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
        if NUM_OF_REQ_BS_IN_URL != num_of_bs_in_url:
            continue

        tdo['id'] = page_url.split('/')[INDEX_OF_ID_IN_URL]

        # get html raw content from crawled data
        curr_html_doc = temp_dict_in['raw_content']
        curr_soup = BeautifulSoup(curr_html_doc, 'html.parser')

        # get publisher
        tdo['publisher'] = get_publisher(curr_soup)

        # skip publisher which aren't Marvel or DC-Comics
        if tdo['publisher'] == None or (tdo['publisher'][0] != DC_COMICS_PUB_ID and tdo['publisher'][0] != MARVEL_PUB_ID):
            continue

        # print progress
        print("Processing[" + str(counter) + "]: " + str(tdo['id']) + " [" + str(page_url) + "]")
        counter += 1

        # find the wiki-details tag
        wikidet_div = curr_soup.findAll("div", {"class": "wiki-details"})[INDEX_OF_WIKI_DT]
        
        # get wiki box details
        th_tr_attr = wikidet_div.find_all(['th', 'tr'])
        tdo['name'], tdo['volume'], tdo['issue_number'], tdo['cover_date'], tdo['in_store_date'] = get_issue_info_from_wiki_details_div(th_tr_attr)

        # get lists of: creators, characters, teams and locations
        wikidet_div = curr_soup.findAll("div", {"class": "wiki-details"})[INDEX_OF_CREATORS_CHARS_TEAMS_LOCATIONS_DT]
        wdo_list = wikidet_div.findAll("div", {"class": "wiki-details-object"})
        tdo['creators'], tdo['characters'], tdo['teams'], tdo['locations'] = get_creators_chars_teams_locations_from_div(wdo_list)

        # get score
        tdo['score'] = get_issue_score(curr_soup)

        # get overview
        tdo['abstract'] = get_abstract(curr_soup)

        # provenance info
        tdo['prov_url'] = page_url
        tdo['prov_timestamp'] = temp_dict_in['timestamp_crawl']

        # serialize constructed dictionary to an output JSON-line
        temp_string = json.dumps(tdo)
        # write/append JSON-line to the output file
        write_file.write(temp_string + '\n')
finally:
    # safely close files
    read_file.close()
    write_file.close()
