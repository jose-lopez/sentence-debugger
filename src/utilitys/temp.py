'''
Created on 5 jul. 2021

@author: jose-lopez
'''

from pathlib import Path
from re import finditer

paths = [str(x) for x in Path(".").glob("**/*.txt")]

debugged_sentences = {}
  
# Building the set of sentences contained in the whole set of files

for file in paths:
    with open(file, 'r', encoding="utf8") as f:
        lines = f.readlines()
        line_count = len(lines)
        print(line_count)
        
    sentence = ""
    sentences = []       
    have_new_sentence = False
    have_another_new_sentence = False
    have_point = False
    have_semi_colon = False 
       
    # Building the set of sentences for a file
    for line in lines:
        
        line.replace("\n", "").strip()
        
        dot_matches =  finditer("[\.]", line)
        
        for match in dot_matches:
            print(match.span())   

        if line.contains("."):
            pos_point = line.index(".")
            have_point = True 
        if line.contains("·"):
            pos_semi_colon = line.index("·")
            have_semi_colon = True
            
            
        if not have_point and not have_semi_colon:
            if not line.isspace():
                sentence = sentence + line + " "
                
        if have_point and not have_semi_colon:
            
            partial_sentence_left = line.split(".")[0]
            partial_sentence_rigth = line.split(".")[1]
            new_sentence = sentence + partial_sentence_left + "."
            have_new_sentence = True
            sentence = partial_sentence_rigth + " "
            
        if not have_point and have_semi_colon:
            
            partial_sentence_left = line.split("·")[0]
            partial_sentence_rigth = line.split("·")[1]
            new_sentence = sentence + partial_sentence_left + "."
            have_new_sentence = True
            sentence = partial_sentence_rigth + " "
            
        if have_point and have_semi_colon:
            
            if pos_point < pos_semi_colon:
                partial_sentence_left = line.split(".")[0]
                partial_sentence_rigth = line.split(".")[1]
                new_sentence = sentence + partial_sentence_left + "."
                have_new_sentence = True
                sentence = partial_sentence_rigth + " "
            else:
                partial_sentence_left = line.split("·")[0]
                partial_sentence_rigth = line.split("·")[1]
                new_sentence = sentence + partial_sentence_left + "."
                have_new_sentence = True
                another_new_sentence = partial_sentence_rigth.split(".")[0]
                have_another_new_sentence = True
                sentence = partial_sentence_rigth.split(".")[1] + " "
               
        if have_new_sentence:
            sentences.append(new_sentence)
            
        if have_another_new_sentence:
            sentences.append(another_new_sentence)
            
    # Building a set of sentences free of lakes from a file
    for sentence in sentences:
        if sentence.contains("["):
            number_of_square_brackets = sentence.count("[")
            
    
    

    