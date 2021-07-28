# -*- coding: utf-8 -*-

'''
Created on 5 jul. 2021

@author: jose-lopez
'''

from pathlib import Path
import re

# paths = [str(x) for x in Path("./corpus-eng").glob("**/*.txt")]
paths = [str(x) for x in Path("./corpus-greek-test").glob("**/*.txt")]

debugged_sentences = {}
all_noisy_sentences = {}

# Method to define the end noisy bracket for a noisy sentence.
def get_end_noisy_bracket(all_lines, noisy_brackets, bracket):
  
    end_bracket = None
    from_bracket = bracket

    while not from_bracket == len(noisy_brackets) - 1:
        to_bracket =  from_bracket + 1       
        end_bracket = noisy_brackets[to_bracket]
        text_in_between = all_lines[noisy_brackets[from_bracket].end():end_bracket.start()]
        text_in_between_sentences = re.split("\.", text_in_between)
        if len(text_in_between_sentences) > 1:
            end_bracket =  noisy_brackets[from_bracket]        
            break
        else:
            from_bracket += 1    
                
    return (to_bracket, end_bracket)

# Building the sets of clean and noisy sentences contained in the whole corpus
for file in paths:
    with open(file, 'r', encoding="utf8") as f:
        lines = f.readlines()        

    clean_sentences = []
    noisy_sentences = []
    pattern = "\[[^\]]+\]"
    noisy_pattern = "¯+|˘+|\d+|\.+|⏓+|–+|-|⏑+"
       
    # Building the sets of clean and noisy sentences for a set of lines (a file)
    all_lines = ''
    
    for line in lines:
        
        if not line == "\n":
            line = line.replace("\n", "").strip()
            
            if line.endswith('-'):
                all_lines += line.strip('-')
            else:
                all_lines += line + " "
                
    # print(all_lines)
                
    noisy_brackets= []
    
    double_bracket_matches = re.finditer(pattern, all_lines)
      
    if double_bracket_matches:
        for double_bracket in double_bracket_matches:
            text_in_bracket = all_lines[double_bracket.start() + 1:double_bracket.end() - 1]
            if re.search(noisy_pattern, text_in_bracket):
                noisy_brackets.append(double_bracket)
                
    noisy_double_brackets = len(noisy_brackets)
                
    if not noisy_brackets:
    
        line_sentences =  re.split('\.', all_lines)
    
        for sentence in line_sentences:
            if not sentence.isspace():
                clean_sentences.append(sentence) 
        
    else: # For a set of lines (a file) with at least a noisy double bracket  
        
        actual_coordinate = 0
        bracket = 0
              
        while not bracket == noisy_double_brackets - 1:
            
            start_noisy_bracket = noisy_brackets[bracket].start()
            before_start_bracket = all_lines[actual_coordinate:start_noisy_bracket]
               
            next_bracket, end_bracket = get_end_noisy_bracket(all_lines, noisy_brackets, bracket)
            
            end_noisy_bracket = end_bracket.end()
            
            if next_bracket < noisy_double_brackets - 1:
                after_end_bracket = all_lines[end_noisy_bracket:noisy_brackets[next_bracket].start()]
            else:
                after_end_bracket = all_lines[end_noisy_bracket:]

            before_start_bracket_sentences = re.split('\.', before_start_bracket)
            after_end_bracket_sentences = re.split('\.', after_end_bracket)
            
            noisy_sentence = before_start_bracket_sentences[-1] + all_lines[start_noisy_bracket:end_noisy_bracket] +  after_end_bracket_sentences[0]
                
            if bracket == 0:
                        
                actual_coordinate += end_noisy_bracket + len(after_end_bracket_sentences[0]) + 1                
                del before_start_bracket_sentences[-1]
                
                noisy_sentences.append(noisy_sentence)
                
                for sentence in before_start_bracket_sentences:
                    if not sentence.isspace():
                        clean_sentences.append(sentence)
                    
            else:
                if len(before_start_bracket_sentences) > 1:                                
                    del before_start_bracket_sentences[-1]
                    for sentence in before_start_bracket_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)
                            actual_coordinate += len(sentence) + 1
                                                      
                actual_coordinate += len(noisy_sentence) + 1
                noisy_sentences.append(noisy_sentence)
            
            if next_bracket == noisy_double_brackets - 1:
                del after_end_bracket_sentences[0]                                        
                for sentence in after_end_bracket_sentences:
                    if not sentence.isspace():
                        clean_sentences.append(sentence) 
                            
            bracket  = next_bracket    
       
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
        
                