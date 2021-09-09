'''
Created on 27 ago. 2021

@author: jose-lopez
'''
import regex
from pathlib import Path
import os
from os import path
if __name__ == '__main__':
    
    root = "./texts/"  
    corpus = root + "corpus"
    debugging = root + "debugging/"
    
    if not path.exists(debugging):
        os.mkdir(debugging)            
        
    files = [str(x) for x in Path(corpus).glob("**/*.txt")]
    
    for file in files:
        
        file_name = file.split("/")[-1]
        
        no_debug = open(debugging + file_name + "_no_debug", 'w', encoding="utf8")
        debug = open(debugging + file_name + "_debug", 'w', encoding="utf8")
        only_ancient = open(debugging + file_name + "_ancient", 'w', encoding="utf8")
        
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()
            
        # --- Building a first version of the debugged files for a corpus --- #
        all_lines = ''        
        for line in lines:
                    
            if not line == "\n":
                line = line.replace("\n", "").strip()   
                                
                if line.endswith('-'):
                    all_lines += line.strip('-')
                else:
                    all_lines += line + " "
        
        no_debug.write(all_lines)
        no_debug.close()
        
        # Removing {} and () metadata blocks
        all_lines = regex.sub(r'[{\(][\(\)<>〈〉,\s—\.\-\d;\p{L}]+[\)}]', '', all_lines).strip()
        
        # Removing ASCII letters and some noisy characters
        all_lines = regex.sub(r'[a-zA-Z0-9]+', '', all_lines)
        
        debug.write(all_lines)
        debug.close()
        
        # Removing non Ancient Greek characters 
        # Using unicode blocks
        all_lines = regex.sub("[^\u1F00-\u1FFF\u0370-\u03FF\.·;\s]", '', all_lines)

        # Removing empty double brackets
        # all_lines = regex.sub(r'(\[\s*\])', '', all_lines)
       
        only_ancient.write(all_lines)
        only_ancient.close()
        