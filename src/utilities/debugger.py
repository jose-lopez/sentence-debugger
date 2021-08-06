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
import time

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
not embraced in double brackets (strange noisy sentences). 
"""
def get_strange(clean_sentences, noisy_sentences):
    strange_sentences = []
    for sentence in clean_sentences:
        if re.search("¯+|˘+|⏓+|–+|-|⏑+|\.\d+\.", sentence):
            noisy_sentences.append(sentence) 
            clean_sentences.remove(sentence)
            strange_sentences.append(sentence)
    return strange_sentences

""" A method to get curated clean sentences. """
def get_curated(clean_sentences):
    curated_sentences = []
    for sentence in clean_sentences:
        if re.search("\[[^\]]+\]", sentence):            
            curated_sentences.append(sentence)
    return curated_sentences

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
                            
        # Moving strange noisy sentences from the set of clean sentences
        strange_sentences = get_strange(clean_sentences, noisy_sentences)
        
        # Defining the set of clean sentences that has been curated
        curated_sentences = get_curated(clean_sentences)
        
        # Setting a new processed corpus file      
        corpus_file["clean"] = clean_sentences
        corpus_file["noisy"] = noisy_sentences
        corpus_file["strange"] = strange_sentences
        corpus_file["curated"] = curated_sentences
        len_sentences =  len(clean_sentences) + len(noisy_sentences) +  len(strange_sentences)
        corpus_file["noise_rate"] = round((len(noisy_sentences) + len(strange_sentences))/len_sentences, 5)
        corpus_file["noise_index"] = round((noisy_double_brackets + len(strange_sentences))/len_sentences, 5)        
                
        # Updating the processed corpus with a new processed file
        corpus.append(copy.deepcopy(corpus_file))
        corpus_file.clear()
        
        print("Processing corpus file {}: {}/{}".format(file_name, len(corpus), len(files)), "\n")  

       
    return corpus

""" reporting a set of sentences """
def report_sentences(sentences, path):
    if len(sentences) > 0:
        file = open(
                path, 'w', encoding="utf8")
        for sentence in sentences:
            file.write(sentence.strip() + "." + "\n")
        file.close()
    
""" reporting the noise related with each file in the corpus """    
def report_noise(corpus, path):
    # print(len(corpus))
    noise_rate_file = "/noise_rate.txt"
    noise_index_file = "/noise_index.txt"
    file_path = path + noise_index_file  
    
    # print("Sorting the corpus' files based on the index of noise......." + "\n")   
    # Sorting the corpus in descending order based on the index of noise  
    corpus.sort(key=lambda x: x["noise_index"], reverse=True)
    
    print("Reporting the corpus' files order based on the index of noise......." + "\n")     
    time.sleep(2)  # To see on console what is happening. 
    report = open(
            file_path, 'w', encoding="utf8")    
    report.write("File:" + "\t" + "\t" + "\t" + "\t" + "Noise rate:" + "\t" + "Noise index:" + "\n") 

    for file in corpus:
        report.write(file["name"] + "\t" + "\t" + str(file["noise_rate"]) + "\t" + "\t" + str(file["noise_index"]) + "\n")
    report.close()
    print("....... done" + "\n")
    time.sleep(2)   
 
    # print("Sorting the corpus' files based on the noise rate......." + "\n")    
    # Sorting the corpus in descending order based on the noise rate
    corpus.sort(key=lambda x: x["noise_rate"], reverse=True)
    
    file_path = path + noise_rate_file
    
    print("Reporting the corpus' files order based on the rate of noise......." + "\n")
    time.sleep(2)
    report = open(
            file_path, 'w', encoding="utf8")    
    report.write("File:" + "\t" + "\t" + "\t" + "\t" + "Noise rate:" + "\t" + "Noise index:" + "\n") 
    for file in corpus:
        report.write(file["name"] + "\t" + "\t" + str(file["noise_rate"]) + "\t" + "\t" + str(file["noise_index"]) + "\n")
    report.close()
    print("....... done" + "\n")         
        
""" Debugging the corpus and reporting the related files' noise """
if __name__ == '__main__':
    
    folders = ["clean", "noisy", "strange", "curated", "report"]
    
    # root = "./corpus_greek_test/"
    root = "./ancient_greek_test/"    
    corpus = root + "corpus"
    noise_file = "/noise_report.txt"
    
    for folder in folders:        
        _path =  root + folder
        if not path.exists(_path):
            os.mkdir(_path)
            
    files = [str(x) for x in Path(corpus).glob("**/*.txt")]
    
    # Debugging the corpus and measuring the related files' noise
    corpus = debugger(files)
    
    # Reporting the different set of sentences and the noise measures.
    print("Reporting the clean, noisy, strange and curated sentences......" + "\n")
    time.sleep(2) # To see on console what is happening.
    for file in corpus:
        file_name = "/" + file["name"]
        for folder in folders:            
            if not folder == "report":
                file_path =  root + folder + file_name
                # Reporting the sets of sentences
                report_sentences(file[folder], file_path)
    
    else:
        # print("Reporting the related files' noise measures......." + "\n")
        time.sleep(4) # To see on console what is happening.
        file_path =  root + folder
        # Reporting the related files' noise measures.
        report_noise(corpus, file_path)
                