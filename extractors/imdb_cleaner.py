import json
import datetime

docs = list()
f = open('../data_raw/imdb.jl', 'r')
for line in f:
    docs.append(json.loads(line))
f.close()
cleaned_docs = list()
date_dict = {'January': 'JAN', 'February': 'FEB', 'March': 'MAR', 'April': 'APR', 'May': 'MAY', 'June': 'JUN',
             'July': 'JUL', 'August': 'AUG', 'September': 'SEP', 'October': 'OCT', 'November': 'NOV', 'December': 'DEC'}
for doc in docs:
    new_doc = dict()
    if 'url' in doc and doc['url'][0]:
        new_doc['url'] = doc['url'][0].strip()

    if 'title' in doc and doc['title'][0]:
        new_doc['title'] = doc['title'][0].strip()

    if 'rate' in doc and doc['rate'][0]:
        new_doc['rate'] = float(doc['rate'][0].strip())

    if 'motion_pic_rate' in doc and doc['motion_pic_rate'][0]:
        new_doc['motion_pic_rate'] = doc['motion_pic_rate'][0].strip()

    if 'story_line' in doc and doc['story_line'][0]:
        new_doc['story_line'] = doc['story_line'][0].strip()

    if 'genres' in doc:
        for i in doc['genres']:
            if i.strip():
                if 'genres' in new_doc:
                    new_doc['genres'].append(i.strip())
                else:
                    new_doc['genres'] = [i.strip()]

    if 'key_words' in doc:
        for i in doc['key_words']:
            if i.strip():
                if 'key_words' in new_doc:
                    new_doc['key_words'].append(i.strip())
                else:
                    new_doc['key_words'] = [i.strip()]

    if 'release_date' in doc:
        max_len = 0
        max_idx = 0
        for i, v in enumerate(doc['release_date']):
            if v.strip():
                length = len(v.strip())
                max_len = max(max_len, len(v.strip()))
                max_idx = i if max_len <= len(v.strip()) else max_idx
        # new_doc['release_date'] = doc['release_date'][max_idx].strip()
        d = doc['release_date'][max_idx].strip().replace(' ', '')[:-5]
        for key in date_dict:
            d = d.lower().replace(key.lower(), date_dict[key])
        try:
            date = datetime.datetime.strptime(d, "%d%b%Y")
            new_doc['release_date'] = str(date)
        except:
            pass
        # print (date)

    if 'characters' in doc:
        for i in doc['characters']:
            if i.strip():
                if 'characters' in new_doc:
                    new_doc['characters'].append(i.strip())
                else:
                    new_doc['characters'] = [i.strip()]

    cleaned_docs.append(new_doc)
# print(cleaned_docs)
f = open('imdb_cleaned.jl', 'w')
for doc in cleaned_docs:
    f.write(json.dumps(doc) + '\n')
f.close()
