'''
    from taxonomy_ids.txt to json
'''
import json
import os
import re
import cPickle
from collections import defaultdict

'''
    Example Line:
    1_1_1   */large_scale_distributed_systems   large_scale_distributed_systems,software_engineering,agile_development,software_development,software_process_improvement,software_process,agile_methods,requirements_engineering,web_services,software_reuse
'''
input_file_path = '../data/scientific_corpus/taxonomy_keywords_method_sp.txt'
phrase_quality_file = open(input_file_path+'_phrase_quality', 'w')

level2category2phrases = defaultdict(dict)

links = []
nodes = dict()
id2path = {}
cnt = 1
with open(input_file_path) as f:
    for line in f:
        meta = re.split(pattern='\t', string=line)
        taxonID = meta[0]
        path_raw = meta[1][2:]
        path = path_raw.rsplit('/', 1)
        keywords = meta[2].strip().split(',')

        if not path:
            continue

        id2path[cnt] = path_raw
        level = taxonID[0]
        nodes[path_raw] = {
            'taxonID': taxonID,
            'level': level,
            'path': meta[1][2:],
            'keywords': keywords,
            'name': path[-1]
        }

        for keyword in meta[2].strip().split(','):
            phrase_quality_file.write(keyword.strip().replace('_', ' ')+'\n')

        level2category2phrases[level][path_raw] = keywords

        if len(path) >= 2:
            links.append((path[0], path_raw))
        cnt += 1

cPickle.dump(level2category2phrases, open('level2category2phrases', 'w'))