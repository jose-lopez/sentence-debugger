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

"""" A Method to define the end noisy bracket for a noisy sentence."""
def get_end_noisy_bracket(all_lines, noisy_brackets, bracket):
  
    end_bracket = None
    from_bracket = bracket

    while  from_bracket < len(noisy_brackets) - 1:
        to_bracket =  from_bracket + 1       
        end_bracket = noisy_brackets[to_bracket]
        text_in_between = all_lines[noisy_brackets[from_bracket].end():end_bracket.start()]
        noisy_blocks = regex.findall("[¯˘⏓\-⏑\d—]+|(\.\s){2,}|(\.){2,}|(—\s){2,}", text_in_between)
        if len(noisy_blocks) == 0:
            text_in_between_sentences = re.split("\.", text_in_between)
            if len(text_in_between_sentences) > 1:
                end_bracket =  noisy_brackets[from_bracket]        
                break
            else:
                from_bracket += 1
        else:
            # print([noisy_block for noisy_block in noisy_blocks], len(noisy_blocks))
            from_bracket += 1     
                
    return (to_bracket, end_bracket)

""" Defining if a piece of text has noisy blocks """
def noisy_blocks_in(text):
    noisy_blocks = regex.findall("[¯˘⏓\-⏑\d—]+|(\.\s){2,}|(\.){2,}|(—\s){2,}", text)
    if noisy_blocks:
        return True
    else:
        return False
""" 
A method to ensure non noisy sentences in the clean sentences set.
This happens when there are sentences in a file with noisy patterns
not embraced in double brackets (strange noisy sentences). 
"""
def get_strange(clean_sentences, noisy_sentences):
    strange_sentences = []
    for sentence in clean_sentences:
        if noisy_blocks_in(sentence):
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
def remove_non_greek(sentences):
    greek_sentences = []           
    for sentence in sentences:
        # ---- Removing non Greek characters --- #
        # sentence = regex.sub(r'[—\.\-;a-zA-Z0-9\(\){}]+', '', sentence).strip()
        # sentence = regex.sub(r'[^α-ωΑ-Ωἀ-Ὠἄ-ὤ\W\[\]]+', '', sentence).strip()
        sentence = regex.sub(r'[⸐⸏?!\—〈〉"{}⸤⸥΄|Ϛݲ§ϛ♃5ᾱᾅὝᾂ̆ᾦ#Ἦ*ᾆ⟩ὋἎὒὮ′̣ϝὯἾ͵ῂüὬ⌋⌈‚•ä+̀ö&–ͅᾕë1͂ῲᾡἇἛἋGϠ¶%ῢ^ἊἯæᾇ\\2ᾁῡἚ̋/⌉Ὢß⌊Ἣ=ῗóΌ`3ï⌞⌟ᾲΆ65ϡ̈4∗Ὣq═òΈϞ○à7áΊᾒ‖~אϟΪϥ›\u200b⁄‹íé⋖ὊÍ9Ἲ̄8{ῧ}Üᾟᾍᾨ―ΉŕὟ⩹✶0Ώᾯᾥᾌ\x8d⟦⟧\x9a¦ᾬἻ£a⋇ῐ¬ÓbῚŒἿἏÉῌᾃ\x98°ΎῈÁ⨆�ç↑ạὛ⏔⏑̅✝ú\x9dᾺụᾢᾓᾘῼùÒSῠϙ─\x90לṕᾣô\x9cῸᾜḿ$⦵⊏ī\x9eֹ\x8eÌćÆ\x8fǁ⊻@ū÷Ҁ∾ῺìῪ\x8c\x81ᾮᾈèÿœῩῊ\x88⊤З♀⊙\xadÄÖᾞߤ⁑⸨\x8aḍ⫯∼źẂ⋆★Ῑᾩ‵ᾎý√⏝⏓⏕ṃ×ȳហḾti¿⥽⥼⊣⊔ӄẉ͎\u070eҏďĎ̠◻ᾰ\ue1c2rƑ̧\x7fេឲិតាỳӕῘLᾙΫẃ☾☿♂♄⊢⋃Ā±TMĹ€║̇čō”]', '', sentence)
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
    pattern = "\[[^\]]+\]"
    noisy_pattern = "[¯˘⏓\-⏑\.\d—\s]+" 
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
                    
        # print(all_lines)   
        
        # Removing {} and () metadata blocks
        all_lines = regex.sub(r'[{\(][〈〉,\s—\.\-\d;\p{L}]+[\)}]', '', all_lines).strip()
        # Removing ASCII letters and some non Greek characters
        all_lines = regex.sub(r'[;a-zA-Z\(\){}]+', '', all_lines)
        
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
            line_sentences = []
            if not noisy_blocks_in(all_lines):
                line_sentences =  re.split('\.', all_lines)
            else:
                print("There are not noisy double brackets in {} file".format(corpus_file["name"])) 
                not_included_files.append(corpus_file["name"])
                
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
                            
        # removing all non greek characters from the clean sentences set
        clean_sentences = remove_non_greek(clean_sentences)
                
        # removing all non greek characters from the noisy sentences set
        noisy_sentences = remove_non_greek(noisy_sentences)
                
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
        if not len_sentences == 0:
            corpus_file["noise_rate"] = round((len(noisy_sentences) + len(strange_sentences))/len_sentences, 5)
            corpus_file["noise_index"] = round((noisy_double_brackets + len(strange_sentences))/len_sentences, 5)             
                
        # Updating the processed corpus with a new processed file
        if not len_sentences == 0:
            corpus.append(copy.deepcopy(corpus_file))
        corpus_file.clear()
    
    print("Total of not included files: {} / {}".format(len(not_included_files), len(files)) + "\n")   
    
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
        for file in rejected:
            not_included.write(file.strip() + "\n")
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
    
    # root = "./corpus_greek_test/"
    # root = "./corpus_greek_first_debug/"
    # root = "./corpus-eng/"
    root = "./ancient_greek_test/"    
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
                