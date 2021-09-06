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
import regex

"""" A Method to define the end noisy block for a noisy sentence."""
def get_end_noisy_block(all_lines, noisy_blocks, block, noisy_pattern):
  
    end_block = None
    from_block = block

    while  from_block < len(noisy_blocks) - 1:
        to_block =  from_block + 1       
        end_block = noisy_blocks[to_block]
        text_in_between = all_lines[noisy_blocks[from_block].end():end_block.start()]
        noisy_blocks_in_between = regex.findall(noisy_pattern, text_in_between)
        if len(noisy_blocks_in_between) == 0:
            text_in_between_sentences = re.split("\.", text_in_between)
            if len(text_in_between_sentences) > 1:
                end_block =  noisy_blocks[from_block]        
                break
            else:
                from_block += 1
        else:
            # print([noisy_block for noisy_block in noisy_blocks], len(noisy_blocks))
            from_block += 1     
                
    return (to_block, end_block)

""" Defining if a piece of text has strange noisy blocks (useful to detect new noisy patterns) """
def strange_noisy_blocks_in(text):
    # The next line must be changed to detect just non Greek characters as noise !!
    # noisy_blocks_in_text = regex.findall("[¯˘⏓\-⏑—]+|(\.\s){2,}|(\.){2,}|(—\s){2,}|(-\s){2,}", text)
    noisy_blocks_in_text = regex.findall("[^\u1F00-\u1FFF\u0370-\u03FF\.,·;'‘’\s\[\]⸤⸥]+", text)
    
    if noisy_blocks_in_text:
        return True
    else:
        return False
    
def get_strange_noisy_blocks_in(text):
    return regex.findall("[^\u1F00-\u1FFF\u0370-\u03FF\.,·;'‘’\s\[\]⸤⸥]+", text)    
""" 
A method to ensure non noisy sentences in the clean sentences set.
This happens when there are sentences in a file with noisy patterns
not embraced in blocks (strange noisy sentences). 
"""
def get_strange(clean_sentences, noisy_sentences):
    strange_sentences = []
    for sentence in clean_sentences:
        if strange_noisy_blocks_in(sentence):
            noisy_sentences.append(sentence) 
            clean_sentences.remove(sentence)
            strange_sentences.append(sentence)
    return strange_sentences

""" A method to get curated clean sentences. """
def get_curated(clean_sentences):
    curated_sentences = []
    for sentence in clean_sentences:
        if re.search("\[[^\]]+\]|⸤[^⸥]+⸥", sentence):            
            curated_sentences.append(sentence)
    return curated_sentences

""" Removing all non Greek characters from a set of sentences. """
def remove_non_greek(sentences, full):
    greek_sentences = []           
    for sentence in sentences:
        # ---- Removing non Greek characters --- #
        # sentence = regex.sub(r'[—\.\-;a-zA-Z0-9\(\){}]+', '', sentence).strip()
        # sentence = regex.sub(r'[^α-ωΑ-Ωἀ-Ὠἄ-ὤ\W\[\]]+', '', sentence).strip()
        if full:
            sentence = regex.sub("[^\u1F00-\u1FFF\u0370-\u03FF\.,·;'‘’\s]", '', sentence)
        else:
            sentence = regex.sub("[^\u1F00-\u1FFF\u0370-\u03FF\.,·;'‘’\s\[\]⸤⸥]", '', sentence)
        # sentence = regex.sub(r'(\[\s*\])', '', sentence)        
        num_of_words = len(regex.findall("[\p{L}\p{M}*]+", sentence))
        
        if num_of_words >= 2:  # Only sentences with two or more words        
            greek_sentences.append(sentence)
    return greek_sentences

""" Building the sets of clean and noisy sentences contained in the corpus"""
def debugger(files):       
    corpus_file = {}
    corpus = []
    not_included_files = []
    # noisy_pattern = "[(\.\s){2,}|(\.){2,}|(—\s){2,}|(-\s){2,}|\[\s+\]"
    noisy_pattern = "(\.\s){2,}|(\.){2,}|(—\s){2,}|(-\s){2,}|\[\s+\]|[¯˘⏓\-⏑—]+"
    
    processed_files = 0
    
    for file in files:
        processed_files += 1
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()               
        file_name = file.split("/")[-1]
        corpus_file["name"] = file_name
        clean_sentences = []
        noisy_sentences = []
        
        print("Processing corpus file {}: {}/{}".format(file_name, processed_files, len(files)), "\n") 
            
        # --- Building the sets of clean and noisy sentences for a set of lines (a file) --- #
        all_lines = ''        
        for line in lines:
                    
            if not line == "\n":
                line = line.replace("\n", "").strip()   
                                
                if line.endswith('-'):
                    all_lines += line.strip('-')
                else:
                    all_lines += line + " "

        # Removing {} and () metadata blocks
        all_lines = regex.sub(r'[{\(][\(\)<>〈〉,\s—\.\-\d;\p{L}]+[\)}]', '', all_lines).strip()
        # Removing ASCII letters and numbers
        all_lines = regex.sub(r'[a-zA-Z0-9]+', '', all_lines)        
        
        print(all_lines)
                                        
        noisy_blocks= []
        
        noisy_block_matches = re.finditer(noisy_pattern, all_lines)

        if noisy_block_matches:
            for block in noisy_block_matches:                
                noisy_blocks.append(block)
                
        length_noisy_blocks = len(noisy_blocks) 
                            
        if not noisy_blocks:            
            line_sentences = []
            """
            if strange_noisy_blocks_in(all_lines):
                print("   There are non-standard noisy blocks in {} file".format(corpus_file["name"]) +"\n")
                strange_noisy_blocks = get_strange_noisy_blocks_in(all_lines)
                not_included_files.append((corpus_file["name"],strange_noisy_blocks))
            else:
            """        
            line_sentences =  re.split('\.', all_lines)   
            for sentence in line_sentences:
                if not sentence.isspace():
                    clean_sentences.append(sentence)
            
        else: # For a set of lines (a file) with at least a noisy block  
            
            current_coordinate = 0
            block = 0
                  
            while block < length_noisy_blocks - 1:
                
                start_noisy_block = noisy_blocks[block].start()
                before_start_block = all_lines[current_coordinate:start_noisy_block]
                   
                # Getting the end noisy block for the noisy sentence in progress and the next noisy block ahead
                next_block, end_block = get_end_noisy_block(all_lines, noisy_blocks, block, noisy_pattern)
                
                end_noisy_block = end_block.end()
                
                if next_block < len(noisy_blocks) - 1:
                    after_end_block = all_lines[end_noisy_block:noisy_blocks[next_block].start()]
                else:
                    after_end_block = all_lines[end_noisy_block:]
    
                before_start_block_sentences = re.split('\.', before_start_block)
                after_end_block_sentences = re.split('\.', after_end_block)
                
                noisy_sentence = before_start_block_sentences[-1] + all_lines[start_noisy_block:end_noisy_block] +  after_end_block_sentences[0]
                    
                if block == 0:
                            
                    current_coordinate += end_noisy_block + len(after_end_block_sentences[0]) + 1                
                    del before_start_block_sentences[-1]
                    
                    noisy_sentences.append(noisy_sentence)
                    
                    for sentence in before_start_block_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)
                        
                else:
                    if len(before_start_block_sentences) > 1:                                
                        del before_start_block_sentences[-1]
                        for sentence in before_start_block_sentences:
                            if not sentence.isspace():
                                clean_sentences.append(sentence)
                                current_coordinate += len(sentence) + 1
                                                          
                    current_coordinate += len(noisy_sentence) + 1
                    noisy_sentences.append(noisy_sentence)
                    
                block  = next_block  
            
            else: # Processing the last noisy block
                end_noisy_block = noisy_blocks[block].end()
                after_end_block = all_lines[end_noisy_block:]
                after_end_block_sentences = re.split('\.', after_end_block)
                
                if current_coordinate < end_noisy_block:
                    start_noisy_block = noisy_blocks[block].start()
                    before_start_block = all_lines[current_coordinate:start_noisy_block]
                    before_start_block_sentences = re.split('\.', before_start_block)
                                     
                    noisy_sentence = before_start_block_sentences[-1] + all_lines[start_noisy_block:end_noisy_block] +  after_end_block_sentences[0]
                    noisy_sentences.append(noisy_sentence)
                    
                    if len(before_start_block_sentences) > 1:                                
                        del before_start_block_sentences[-1]
                        for sentence in before_start_block_sentences:
                            if not sentence.isspace():
                                clean_sentences.append(sentence)
                
                if len(after_end_block_sentences)  > 1:
                    del after_end_block_sentences[0] 
                    # print(len(after_end_block_sentences))
                    for sentence in after_end_block_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)
        
        # Defining the set of clean sentences that has been curated
        curated_sentences = get_curated(clean_sentences)
                            
        # removing all non greek characters from the clean sentences set
        clean_sentences = remove_non_greek(clean_sentences, True)
                
        # removing all non greek characters from the noisy sentences set
        # noisy_sentences = remove_non_greek(noisy_sentences, True)
                
        # Moving strange noisy sentences from the set of clean sentences
        strange_sentences = get_strange(clean_sentences, noisy_sentences)
        
        # removing all non greek characters from the set of curated sentences except [] and ⸤⸥
        curated_sentences = remove_non_greek(curated_sentences, False)
        
        # Setting a new processed corpus file      
        corpus_file["clean"] = clean_sentences
        corpus_file["noisy"] = noisy_sentences
        corpus_file["strange"] = strange_sentences
        corpus_file["curated"] = curated_sentences
        len_sentences =  len(clean_sentences) + len(noisy_sentences) +  len(strange_sentences)
        if not len_sentences == 0:
            corpus_file["noise_rate"] = round((len(noisy_sentences) + len(strange_sentences))/len_sentences, 5)
            corpus_file["noise_index"] = round((len(noisy_blocks) + len(strange_sentences))/len_sentences, 5)             
                
        # Updating the processed corpus with a new processed file
        if not len_sentences == 0:
            corpus.append(copy.deepcopy(corpus_file))
        corpus_file.clear()
    
    print("Excluded files: {} / {}".format(len(not_included_files), len(files)) + "\n")   
    
    return (corpus, not_included_files)

""" reporting a set of sentences """
def report_sentences(sentences, path):
    if len(sentences) > 0:
        file = open(
                path, 'w', encoding="utf8")
        for sentence in sentences:
            file.write(sentence.strip() + "." + "\n")
        file.close()
        
""" Reporting the rejected files"""
def report_rejected(rejected, path):
    rejected_path = path + "/not_included_files.txt"
    if len(rejected) > 0:
        not_included = open(
                rejected_path, 'w', encoding="utf8")
        
        print("Reporting the set of not included corpus' files......." + "\n")     
        for file, strange_noisy_blocks in rejected:
            not_included.write(file.strip() + "\n")
            for strange_noisy_block in strange_noisy_blocks:
                not_included.write(strange_noisy_block + " ")
        not_included.close()
        time.sleep(2)  # To see on console what is happening. 
        print("....... done")
    
""" Reporting the noise related to each file in the corpus """    
def report_noise(corpus, path):
    # print(len(corpus))
    noise_rate_file = "/noise_rate.txt"
    noise_index_file = "/noise_index.txt"
    file_path = path + noise_index_file  
    
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
    
    root = "./corpus_greek_test/"
    # root = "./corpus_greek_first_debug/"
    # root = "./corpus-eng/"
    # root = "./ancient_greek_test/"    
    corpus = root + "corpus"   
    
    for folder in folders:        
        _path =  root + folder
        if not path.exists(_path):
            os.mkdir(_path)
            
    files = [str(x) for x in Path(corpus).glob("**/*.txt")]
    
    # Debugging the corpus and measuring the related files' noise
    # Also getting the not included (yet) files
    corpus, rejected = debugger(files)
    
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

        _path =  root + folder
        # Reporting the related files' noise measures.
        report_noise(corpus, _path)
        report_rejected(rejected, _path)