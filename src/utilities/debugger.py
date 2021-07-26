# -*- coding: utf-8 -*-

'''
Created on 5 jul. 2021

@author: jose-lopez
'''

from pathlib import Path
import re

paths = [str(x) for x in Path("./corpus-eng").glob("**/*.txt")]

debugged_sentences = {}
all_noisy_sentences = {}

def get_next_noisy_bracket(all_lines, noisy_brackets, bracket, num_of_noisy_double_brackets):
  
    next_noisy_bracket = None
    from_bracket = bracket

    while not from_bracket == num_of_noisy_double_brackets - 1:
        to_bracket =  from_bracket + 1       
        next_noisy_bracket = noisy_brackets[to_bracket]
        text_in_between = all_lines[noisy_brackets[from_bracket].end():next_noisy_bracket.start()]
        text_between_sentences = re.split("\.", text_in_between)
        if len(text_between_sentences) > 1:
            next_noisy_bracket =  noisy_brackets[from_bracket]        
            break
        else:
            from_bracket += 1    
                
    return (to_bracket, next_noisy_bracket)

# Building the sets of clean and noisy sentences contained in the whole corpus

for file in paths:
    with open(file, 'r', encoding="utf8") as f:
        lines = f.readlines()        

    clean_sentences = []
    noisy_sentences = []
    pattern = "\[[^\]]+\]"
    noisy_pattern = "¯+|˘+|\d+|\.+"
       
    # Building the sets of clean and noisy sentences for a file
    all_lines = ''
    for line in lines:
        
        if not line == "\n" and not line.startswith("{") and not line.endswith("}"):
            line = line.replace("\n", "").strip()
            
            if line.endswith('-'):
                all_lines += line.strip('-')
            else:
                all_lines += line + " "
                
    noisy_brackets= []
    
    double_bracket_matches = re.finditer(pattern, all_lines)
      
    if double_bracket_matches:
        for double_bracket in double_bracket_matches:
            text_in_bracket = all_lines[double_bracket.start() + 1:double_bracket.end() - 1]
            if re.search(noisy_pattern, text_in_bracket):
                noisy_brackets.append(double_bracket)
                
    num_of_noisy_double_brackets = len(noisy_brackets)
                
    if not noisy_brackets:
    
        line_sentences =  re.split('\.', all_lines)
    
        for sentence in line_sentences:
            if not sentence.isspace():
                clean_sentences.append(sentence) 
        
    else: # For a set of lines with at least a noisy double bracket  
        
        actual_coordinate = 0
        bracket = 0
              
        while not bracket == num_of_noisy_double_brackets - 1:
            
            start_noisy_bracket = noisy_brackets[bracket].start()
            before_bracket = all_lines[actual_coordinate:start_noisy_bracket]
               
            new_bracket, next_noisy_bracket = get_next_noisy_bracket(all_lines, noisy_brackets, bracket, num_of_noisy_double_brackets)
            
            end_noisy_bracket = next_noisy_bracket.end()
            
            if new_bracket < num_of_noisy_double_brackets - 1:
                rest_of_the_line = all_lines[end_noisy_bracket:noisy_brackets[new_bracket].start()]
            else:
                rest_of_the_line = all_lines[end_noisy_bracket:]

            before_bracket_sentences = re.split('\.', before_bracket)
            rest_of_the_line_sentences = re.split('\.', rest_of_the_line)
            
            noisy_sentence = before_bracket_sentences[-1] + all_lines[start_noisy_bracket:end_noisy_bracket] +  rest_of_the_line_sentences[0]
                
            if bracket == 0 and not bracket == num_of_noisy_double_brackets - 1:
                        
                actual_coordinate += end_noisy_bracket + len(rest_of_the_line_sentences[0]) + 1                
                del before_bracket_sentences[-1]
                
                noisy_sentences.append(noisy_sentence)
                
                for sentence in before_bracket_sentences:
                    if not sentence.isspace():
                        clean_sentences.append(sentence)
                    
            elif not bracket == num_of_noisy_double_brackets - 1:
                if len(before_bracket_sentences) > 1:                                
                    del before_bracket_sentences[-1]
                    for sentence in before_bracket_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)
                            actual_coordinate += len(sentence) + 1
                                                      
                actual_coordinate += len(noisy_sentence) + 1
                noisy_sentences.append(noisy_sentence)
                
                if new_bracket == num_of_noisy_double_brackets - 1:
                    del rest_of_the_line_sentences[0]                                        
                    for sentence in rest_of_the_line_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence) 
                            
            bracket  = new_bracket    
       
    debugged_sentences[file] = clean_sentences   
    all_noisy_sentences[file] = noisy_sentences
    
for file, clean_sentences in debugged_sentences.items():
    
    print("Clean sentences for file {} :  (Total/{})".format(file,len(clean_sentences)))
    for clean_sentence in clean_sentences:
        print (clean_sentence.strip())
        
for file, noisy_sentences in all_noisy_sentences.items():
    
    print("Noisy sentences for file {} :  (Total/{}) ".format(file,len(noisy_sentences)))
    for noisy_sentence in noisy_sentences:
        print (noisy_sentence.strip())            
        
                