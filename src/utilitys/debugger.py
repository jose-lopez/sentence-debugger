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

  
# Building the sets of clean and noisy sentences contained in the whole corpus
for file in paths:
    with open(file, 'r', encoding="utf8") as f:
        lines = f.readlines()

        
    sentence_in_progress = ""
    clean_sentences = []
    noisy_sentences = []
    pattern = "\[[^\]]+\]"
    single_pattern = "\[[¯+|˘+|\d+|\.+]"
    noisy_pattern = "¯+|˘+|\d+|\.+"
    sentence_in_progress_is_noisy = False
    number_of_lines = 0
       
    # Building the sets of clean and noisy sentences for a file
    for line in lines:
        
        noisy_line = False
        number_of_lines += 1 

        if not line == "\n" and not line.startswith("{") and not line.endswith("}"):
            
            line = line.replace("\n", "").strip()
            
            double_brackets = False
            single_brackets = False   
            
            double_bracket_matches = re.finditer(pattern, line)
            
            if double_bracket_matches:
                for double_bracket in double_bracket_matches:
                    text_in_bracket = line[double_bracket.start() + 1:double_bracket.end() - 1]
                    if re.search(noisy_pattern, text_in_bracket):
                        noisy_line = True
                        double_brackets = True
                        break
                        
            if not double_brackets:
                    
                single_bracket_matches = re.finditer("\[", line)
                for single_bracket in single_bracket_matches:
                    text_from_bracket = line[single_bracket.start() + 1:]
                    if text_from_bracket.count("."):
                        text_to_check = text_from_bracket[:text_from_bracket.index(".")]
                    else:
                        text_to_check = text_from_bracket
                    if re.search(noisy_pattern, text_to_check):
                        noisy_line = True
                        single_bracket = True
                        break
                        
                noisy_single_beackets = re.findall("\[[¯+|˘+|\d+|\.+]", line)
                
                if len(noisy_single_beackets) > 1:
                    print("Transcription error: Noisy line with more than one open noisy bracket in file {}: line {}".format(file, number_of_lines))
                    print("Please, fix the line and run the script again")
                    exit()
                        
            if not noisy_line:
            
                line_sentences =  re.split('\.', line)
            
                if len(line_sentences) > 1:
                    line_sentences[0] = sentence_in_progress + line_sentences[0]
                else:
                    line = sentence_in_progress + line
            
                if len(line_sentences) > 1:
                    last_sentence = line_sentences[-1]
                    if last_sentence.endswith("-"):
                        sentence_in_progress = last_sentence.strip("-")
                    else:
                        sentence_in_progress = last_sentence + " "
                    if sentence_in_progress_is_noisy:
                        noisy_sentences.append(line_sentences[0].strip())
                        del line_sentences[0]
                        sentence_in_progress_is_noisy = False
                    for sentence_at in range(len(line_sentences) - 1):
                        clean_sentences.append(line_sentences[sentence_at].strip()) 
                elif line.endswith("-"):
                    sentence_in_progress = line.strip("-")            
                else:
                    sentence_in_progress = line + " "
                
            elif double_brackets: # For a line with at least a noisy double bracket
                
                noisy_brackets= []
                double_bracket_matches = re.finditer(pattern, line)
                
                for double_bracket in double_bracket_matches:
                    text_in_bracket = line[double_bracket.start() + 1:double_bracket.end() - 1]          
                    noisy_bracket = re.search(noisy_pattern, text_in_bracket)
                    if noisy_bracket:
                        noisy_brackets.append(double_bracket)
                        
                num_of_double_brackets = len(noisy_brackets)
                
                actual_coordinate = 0
                      
                for bracket in range(num_of_double_brackets):
                    
                    start_noisy_bracket = noisy_brackets[bracket].start()
                    end_noisy_bracket = noisy_brackets[bracket].end()
                    before_bracket = line[actual_coordinate:start_noisy_bracket]
                    rest_of_the_line = line[end_noisy_bracket:]
                    rest_of_the_line_sentences = re.split('\.', rest_of_the_line)
                    before_bracket_sentences = re.split('\.', before_bracket)
                        
                    noisy_sentence = before_bracket_sentences[-1] + " " + line[start_noisy_bracket:end_noisy_bracket] + rest_of_the_line_sentences[0]
                    
                    if len(before_bracket_sentences) > 1 and len(rest_of_the_line_sentences) > 1:
                        noisy_sentence_active = True
                    else:
                        noisy_sentence_active = False
                        
                    if bracket == 0 and not bracket == num_of_double_brackets -1:
                        
                        if len(before_bracket_sentences) > 1:
                            actual_coordinate += len(before_bracket_sentences[0]) + 1
                            before_bracket_sentences[0] = sentence_in_progress + before_bracket_sentences[0]
                            del before_bracket_sentences[-1]
                        else: 
                            actual_coordinate += len(before_bracket_sentences[0]) + len(line[start_noisy_bracket:end_noisy_bracket]) + len(rest_of_the_line_sentences[0]) + 1                         
                            before_bracket_sentences[0] = sentence_in_progress + before_bracket_sentences[0] +  " " + line[start_noisy_bracket:end_noisy_bracket] +  rest_of_the_line_sentences[0]
                            # noisy_sentence_active = False 
                 
                        if sentence_in_progress_is_noisy == True:
                            noisy_sentences.append(before_bracket_sentences[0])
                        else:
                            clean_sentences.append(before_bracket_sentences[0])
                        
                        del before_bracket_sentences[0]
                        
                        for sentence in before_bracket_sentences:
                            clean_sentences.append(sentence)
                            actual_coordinate += len(before_bracket_sentences[0]) + 1
                            

                        if before_bracket == '': # Border condition: The first bracket is at the beginning of the sentence
                            pass
                        else:
                            if noisy_sentence_active:
                                actual_coordinate += len(noisy_sentence)
                                noisy_sentences.append(noisy_sentence)

                    else: # When the double noisy bracket is different from the first and the last
                        
                        if not bracket == num_of_double_brackets - 1:
                            if len(before_bracket_sentences) > 1:                                
                                del before_bracket_sentences[-1]
                                for sentence in before_bracket_sentences:
                                    clean_sentences.append(sentence)
                                    actual_coordinate += len(before_bracket_sentences[0]) + 1                              
                            actual_coordinate += len(noisy_sentence)
                            noisy_sentences.append(noisy_sentence)
                            
                        else: # Processing the last double noisy bracket in a line with more than one
              
                            single_noisy_match = re.search(single_pattern, rest_of_the_line)
                            
                            if single_noisy_match == None:
                                
                                if len(rest_of_the_line_sentences) > 1:
                                    noisy_sentences.append(noisy_sentence)
                                    noisy_text = rest_of_the_line_sentences[-1]
                                    
                                    del before_bracket_sentences[0]
                                        
                                    if len(before_bracket_sentences) >= 1:                                
                                        del before_bracket_sentences[-1]
                                    
                                    for sentence in before_bracket_sentences:
                                        clean_sentences.append(sentence)
                                        
                                    del rest_of_the_line_sentences[0] 
                                    
                                    del rest_of_the_line_sentences[-1]
                                    
                                    for sentence in rest_of_the_line_sentences:
                                        clean_sentences.append(sentence)

                                    sentence_in_progress_is_noisy = False
                                else:
                                    noisy_text = noisy_sentence
                                    sentence_in_progress_is_noisy = True
                            else:
                                before_single_bracket = rest_of_the_line[:single_noisy_match.start()]
                                after_single_bracket = rest_of_the_line[single_noisy_match.start():]
                                before_single_bracket_sentences = before_single_bracket.split(".")
                                
                                if len(before_single_bracket_sentences) >=2:
                                    noisy_sentence = before_bracket_sentences[0]+ " " + line[start_noisy_bracket:end_noisy_bracket] + before_single_bracket_sentences[0]
                                    noisy_text = before_single_bracket_sentences[-1] + after_single_bracket
                                    noisy_sentences.append(noisy_sentence)                                
                                elif len(before_single_bracket_sentences) == 1:
                                    noisy_text = before_bracket_sentences[-1] + " " + line[start_noisy_bracket:end_noisy_bracket] + before_single_bracket + after_single_bracket
                               
                                del before_single_bracket_sentences[0]
                                if len(before_single_bracket_sentences) >= 1:                                
                                    del before_single_bracket_sentences[-1]
                                
                                for sentence in before_single_bracket_sentences:
                                    clean_sentences.append(sentence)
                                    
                                sentence_in_progress_is_noisy = True
                                    
                            if noisy_text.endswith("-"):
                                sentence_in_progress = noisy_text.strip("-")
                            else:
                                sentence_in_progress = noisy_text + " "
                
                            
            elif single_bracket:# When the line has just a one open single noisy bracket.
        
                single_noisy_match = re.search("\[[¯+|˘+|\d+|\.+]", line)
                before_single_bracket = line[:single_noisy_match.start()]
                before_single_bracket_sentences = before_single_bracket.split(".")
                before_single_bracket_sentences[0] = sentence_in_progress + before_single_bracket_sentences[0]
                sentence_in_progress = before_single_bracket_sentences[-1] + line[single_noisy_match.start():]                

                if sentence_in_progress_is_noisy:
                    noisy_sentences.append(before_single_bracket_sentences[0])
                    del before_single_bracket_sentences[0]
                    
                del before_single_bracket_sentences[-1]
                
                for sentence in before_single_bracket_sentences:
                    clean_sentences.append(sentence.strip())
                    
                sentence_in_progress_is_noisy = True
   
        print(len(clean_sentences))
        print(len(noisy_sentences))
    
       
    debugged_sentences[file] = clean_sentences    
    all_noisy_sentences[file] = noisy_sentences
    
    for file, clean_sentences in debugged_sentences.items():
        
        print("Clean sentences for file {} :  ".format(file))
        for clean_sentence in clean_sentences:
            print (clean_sentence.strip())
            
    for file, noisy_sentences in all_noisy_sentences.items():
        
        print("Noisy sentences for file {} ".format(file))
        for noisy_sentence in noisy_sentences:
            print (noisy_sentence.strip())            
        
                