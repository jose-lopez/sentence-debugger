# -*- coding: utf-8 -*-

'''
Created on 5 jul. 2021

@author: jose-lopez
'''

from pathlib import Path
import re
import copy
import os
from os import path

"""" A Method to define the end noisy bracket for a noisy sentence."""
def get_end_noisy_bracket(all_lines, noisy_brackets, bracket):
  
    end_bracket = None
    from_bracket = bracket

    while  from_bracket < len(noisy_brackets) - 1:
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

""" 
A method to ensure non noisy sentences in the clean sentences set.
This happens when there are sentences in a file with noisy patterns
not embraced in double brackets. 
"""
def check_clean(clean_sentences, noisy_sentences):
    index = 0
    to_delete = []
    for sentence in clean_sentences:
        if re.search("¯+|˘+|\d+|⏓+|–+|-|⏑+", sentence):
            to_delete.append(index)
        index += 1 
    for item in to_delete:
        noisy_sentences.append(clean_sentences[item]) 
        del clean_sentences[item]
                                 
    return len(to_delete)

""" Building the sets of clean and noisy sentences contained in the corpus"""
def debugger(files):   

    corpus_file = {}
    corpus = []
    pattern = "\[[^\]]+\]"
    noisy_pattern = "¯+|˘+|\d+|\.+|⏓+|–+|-|⏑+"
    
    for file in files:
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()               
        file_name = file.split("/")[-1]
        corpus_file["name"] = file_name
        clean_sentences = []
        noisy_sentences = []
            
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
            
            current_coordinate = 0
            bracket = 0
                  
            while bracket < noisy_double_brackets - 1:
                
                start_noisy_bracket = noisy_brackets[bracket].start()
                before_start_bracket = all_lines[current_coordinate:start_noisy_bracket]
                   
                # Getting the end double noisy bracket for the noisy sentence in progress and the next noisy bracket ahead
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
                            
                    current_coordinate += end_noisy_bracket + len(after_end_bracket_sentences[0]) + 1                
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
                                current_coordinate += len(sentence) + 1
                                                          
                    current_coordinate += len(noisy_sentence) + 1
                    noisy_sentences.append(noisy_sentence)
                    
                bracket  = next_bracket  
            
            else: # Processing the last noisy double bracket
                end_noisy_bracket = noisy_brackets[bracket].end()
                after_end_bracket = all_lines[end_noisy_bracket:]
                after_end_bracket_sentences = re.split('\.', after_end_bracket)
                
                if current_coordinate < end_noisy_bracket:
                    start_noisy_bracket = noisy_brackets[bracket].start()
                    before_start_bracket = all_lines[current_coordinate:start_noisy_bracket]
                    before_start_bracket_sentences = re.split('\.', before_start_bracket)
                                     
                    noisy_sentence = before_start_bracket_sentences[-1] + all_lines[start_noisy_bracket:end_noisy_bracket] +  after_end_bracket_sentences[0]
                    noisy_sentences.append(noisy_sentence)
                    
                    if len(before_start_bracket_sentences) > 1:                                
                        del before_start_bracket_sentences[-1]
                        for sentence in before_start_bracket_sentences:
                            if not sentence.isspace():
                                clean_sentences.append(sentence)
                
                if len(after_end_bracket_sentences)  > 1:
                    del after_end_bracket_sentences[0] 
                    # print(len(after_end_bracket_sentences))
                    for sentence in after_end_bracket_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)
        # Checking the set of clean sentences
        # check_clean(clean_sentences, noisy_sentences)
        
        # Updating the corpus with a new processed file           
        corpus_file["clean_sentences"] = clean_sentences
        corpus_file["noisy_sentences"] = noisy_sentences
        corpus_file["size"] = len(clean_sentences) + len(noisy_sentences)
        corpus_file["size_clean"] = len(clean_sentences)
        corpus_file["size_noisy"] = len(noisy_sentences)
        corpus_file["noise_rate"] = round(corpus_file["size_noisy"]/corpus_file["size"], 3)
        corpus_file["noise_index"] = round(noisy_double_brackets/corpus_file["size"], 3)        
        
        corpus.append(copy.deepcopy(corpus_file))
        
        print("Processing corpus file {}: {}/{}".format(file_name, len(corpus), len(files)), "\n")
   
    print("Sorting the corpus' files based on index of noise")    
    # Sorting the corpus in descending order based on the noise rate    
    corpus.sort(key=lambda x: x["noise_index"], reverse=True) 
       
    return corpus

""" reporting a set of sentences """
def report_sentences(sentences, path):
    file = open(
            path, 'w', encoding="utf8")
    for sentence in sentences:
        file.write(sentence.strip() + "." + "\n")
    file.close()
    
""" reporting the noise related with each file in the corpus """    
def report_noise_rate(corpus, path):
    # print(len(corpus))
    report = open(
            path, 'w', encoding="utf8")
    report.write("File:" + "\t" + "\t" + "\t" + "\t" + "Noise rate:" + "\t" + "Noise index:" + "\n") 
    print("File:" + "\t" + "\t" + "\t" + "\t" + "Noise rate:" + "\t" + "Noise index:" + "\n")     
    for file in corpus:
        report.write(file["name"] + "\t" + "\t" + str(file["noise_rate"]) + "\t" + "\t" + str(file["noise_index"]) + "\n")
        print(file["name"] + "\t" + "\t" + str(file["noise_rate"]) + "\t" + "\t" + str(file["noise_index"]) + "\n")
    report.close()
        
""" Debugging the corpus and reporting the related files' noise """
if __name__ == '__main__':
    
    # root = "./corpus_greek_test/"
    root = "./ancient_greek_test/"    
    corpus = root + "corpus/"
    path_report = root + "report/"
    path_clean_sentences = root + "clean/"
    path_noisy_sentences = root + "noisy/"     
    if not path.exists(path_report):
        os.mkdir(path_report)
    if not path.exists(path_clean_sentences):        
        os.mkdir(path_clean_sentences)
        os.mkdir(path_noisy_sentences)
            
    files = [str(x) for x in Path(corpus).glob("**/*.txt")]
    
    # Debugging the corpus and measuring the related files' noise
    corpus = debugger(files)
    
    # Reporting the clean and noisy sentences in the corpus
    for file in corpus:
        path_file =  path_clean_sentences + file["name"]
        report_sentences(file["clean_sentences"], path_file)
        path_file =  path_noisy_sentences + file["name"]
        report_sentences(file["noisy_sentences"], path_file)
        
    # Reporting the related files' noise
    report_noise_rate(corpus, path_report + "noisy_rate.txt")
                