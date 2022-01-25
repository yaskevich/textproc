#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import errno
import sys
import requests
import json
from conllu import parse


file_results = 'report.txt'
cwd = os.getcwd()
endpoint = 'http://lindat.mff.cuni.cz/services/udpipe/api/process'
data_dir = os.path.join(cwd, "data")

try:
    os.mkdir(os.path.join(cwd, "api"))
except OSError as error:
    if error.errno != errno.EEXIST:
        raise
    pass
    
if not os.path.isdir(data_dir):
    print("Data directory was not found!")
    sys.exit()

report = open(os.path.join(cwd, file_results), 'w', encoding='utf-8')
divider = "=" * 100

for file in os.listdir(data_dir):
    bigpos = {}
    
    f = open(os.path.join(data_dir, file), encoding='utf-8')
    lines = f.readlines()
    f.close()
    
    group = file[:-4].upper()
    
    report.write(divider + '\n' + group + '\n' + divider + '\n')
    
    for index, line in enumerate(lines):
        # print(line)
        arr = [i.strip() for i in line.split("\t")]
        # print("file", arr[0])
        # OrderedDict([('id', 79), ('form', 'бегать'), ('lemma', 'бегать'), ('upostag', 'VERB'), ('xpostag', None), ('feats', 
        
        conll_file = os.path.join(cwd, "api", arr[0])
        conll_content = ""
        pos = {}
        
        print(("/" if index%2 else "\\") + "\r", end = "")
        
        report.write('\n' + arr[0] + '\n')
        if os.path.isfile(conll_file):
            with open(os.path.join(cwd, conll_file), 'r', encoding='utf8') as f:
                conll_content = f.read()
                # print(arr[0], "read")
        else:
            print("●", arr[0])
            
            request_params = {
                "tokenizer": '', 
                "tagger": '', 
                "model": "russian-syntagrus-ud-2.6-200830",
                "data": arr[1]
            }
            
            r = requests.post(endpoint, data = request_params)
            if r.status_code == 200:
                datum = r.json()
                # with open(os.path.join(cwd, conll_file), 'w', encoding='utf-8') as f:
                    # json.dump(datum, f, ensure_ascii=False, indent=4)
                
                # print(arr[0], "write")
                conll_content = datum["result"]
                with open(os.path.join(cwd, conll_file), 'w', encoding='utf8') as f:
                    f.write(conll_content)
            
        if conll_content:
            ud = parse(conll_content)
            for token in ud[0]:
                tag = token["upostag"]
                if tag == "PROPN":
                    tag = "NOUN"
                lemma = token["lemma"].lower()
                # print(lemma, tag, end =" ")
                pos_cur = pos.get(tag,[])
                pos_cur.append(lemma)
                pos[tag] = pos_cur
                
                big_cur = bigpos.get(tag,[])
                big_cur.append(lemma)
                bigpos[tag] = big_cur
                
            # print(pos)
            # print("=======================")
            pos_uniq = {}
            
            for key, value in pos.items():
                pos_uniq[key] = list(set(value))
            
            desc = sorted(pos.items(), key=lambda x: len(x[1]), reverse=True)
            desc_uniq = sorted(pos_uniq.items(), key=lambda x: len(x[1]), reverse=True)
            
            
            # print (desc)
            report.write("...Occurencies\n")
            
            for x in desc:
                # print(x[0].ljust(10), str(len(x[1])).ljust(10), ', '.join(x[1]))
                report.write('\t' + x[0].ljust(10) + str(len(x[1])).ljust(10) + ', '.join(x[1]) + "\n")
            
            report.write("\n...Lexemes\n")
            
            verbs = 0
            nonverbs = 0
            nonnouns = 0
            nouns = 0
            
            for x in desc_uniq:
                # print(x[0].ljust(10), str(len(x[1])).ljust(10), ', '.join(x[1]))
                report.write('\t' + x[0].ljust(10) + str(len(x[1])).ljust(10) + ', '.join(x[1]) + "\n")
                
                if x[0] == 'VERB':
                    verbs += len(x[1])
                
                if x[0] != 'VERB':
                    nonverbs += len(x[1])
                    
                if x[0] == 'NOUN':
                    nouns += len(x[1])
                
                if x[0] != 'NOUN':
                    nonnouns += len(x[1])
                
            # print(x[0])
            report.write("\n...stats\n")
            report.write('\t' + "verbs".ljust(10) + str(verbs).ljust(10) + "\n")
            report.write('\t' + "nonverbs".ljust(10) + str(nonverbs).ljust(10) + "\n")
            
            report.write('\t' + "verbs/nonverbs".ljust(10) + "\t" + (str(round(verbs/nonverbs*100, 2))+ "%").ljust(20) + "\n")
            report.write("\n")
            report.write('\t' + "nouns".ljust(10) + str(nouns).ljust(10) + "\n")
            report.write('\t' + "nonnouns".ljust(10) + str(nonnouns).ljust(10) + "\n")
            
            report.write('\t' + "nouns/nonnouns".ljust(10) + "\t" + (str(round(nouns/nonnouns*100, 2))+ "%").ljust(20) + "\n")
        
    report.write("\n\n---------------------------------\n")
    report.write("Total for «" + group + '»')
    report.write("\n---------------------------------\n")
    
    bigpos_uniq = {}
    
    for key, value in bigpos.items():
        bigpos_uniq[key] = list(set(value))
        
    big_desc = sorted(bigpos.items(), key=lambda x: len(x[1]), reverse=True)
    big_desc_uniq = sorted(bigpos_uniq.items(), key=lambda x: len(x[1]), reverse=True)
    
    report.write("...Occurencies\n")
    for x in big_desc:
        report.write('\t' + x[0].ljust(10) + str(len(x[1])).ljust(10) + ', '.join(x[1]) + "\n\n")
    report.write("\n...Lexemes\n")
    for x in big_desc_uniq:
        report.write('\t' + x[0].ljust(10) + str(len(x[1])).ljust(10) + ', '.join(x[1]) + "\n\n")    
    report.write("\n")


    bigverbs = 0
    bignonverbs = 0
    bignonnouns = 0
    bignouns = 0
            
    for x in big_desc:
        if x[0] == 'VERB':
            bigverbs += len(x[1])
        
        if x[0] != 'VERB':
            bignonverbs += len(x[1])
            
        if x[0] == 'NOUN':
            bignouns += len(x[1])
        
        if x[0] != 'NOUN':
            bignonnouns += len(x[1])

    report.write("\n...global stats\n")
    report.write('\t' + "verbs".ljust(10) + str(bigverbs).ljust(10) + "\n")
    report.write('\t' + "nonverbs".ljust(10) + str(bignonverbs).ljust(10) + "\n")
    
    report.write('\t' + "verbs/nonverbs".ljust(10) + "\t" + (str(round(bigverbs/bignonverbs*100, 2))+ "%").ljust(20) + "\n")
    report.write("\n")
    report.write('\t' + "nouns".ljust(10) + str(nouns).ljust(10) + "\n")
    report.write('\t' + "nonnouns".ljust(10) + str(nonnouns).ljust(10) + "\n")
    
    report.write('\t' + "nouns/nonnouns".ljust(10) + "\t" + (str(round(nouns/nonnouns*100, 2))+ "%").ljust(20) + "\n")

print("Done!")
report.close()        