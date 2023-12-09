# -*- coding: utf-8 -*-

'''
Created on 15 Nov. 2023
@author: jose-lopez
'''

import copy
from os import path
import os
from pathlib import Path
import re
import shutil
import sys
import time

import regex


def get_end_noisy_block(all_lines, noisy_blocks, block, noisy_pattern):
    """" A Method to define the end noisy block for a noisy sentence."""

    end_block = None
    from_block = block

    while from_block < len(noisy_blocks) - 1:
        to_block = from_block + 1
        end_block = noisy_blocks[to_block]
        text_in_between = all_lines[noisy_blocks[from_block].end(
        ):end_block.start()]
        noisy_blocks_in_between = regex.findall(noisy_pattern, text_in_between)
        if len(noisy_blocks_in_between) == 0:
            text_in_between_sentences = re.split("\.", text_in_between)
            if len(text_in_between_sentences) > 1:
                end_block = noisy_blocks[from_block]
                break
            else:
                from_block += 1
        else:
            from_block += 1

    return (to_block, end_block)


def strange_noisy_blocks_in(text):
    """
    Defining if a piece of text has strange
    noisy blocks (useful to detect new noisy patterns)
    """

    noisy_blocks_in_text = regex.findall(
        "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s\[\]⸤⸥]+", text)

    if noisy_blocks_in_text:
        return True
    else:
        return False


def get_strange_noisy_blocks_in(text):
    return regex.findall("[^\u1F00-\u1FFF\u0370-\u03FF\.'\s\[\]⸤⸥]+", text)


def get_strange(clean_sentences, noisy_sentences):
    """
    A method to ensure non noisy sentences in the clean sentences set.
    This happens when there are sentences in a file with noisy patterns
    not embraced in blocks (strange noisy sentences).
    """
    strange_sentences = []
    for sentence in clean_sentences:
        if strange_noisy_blocks_in(sentence):
            noisy_sentences.append(sentence)
            clean_sentences.remove(sentence)
            strange_sentences.append(sentence)
    return strange_sentences


def get_curated(clean_sentences):
    """
     A method to get curated clean sentences.
    """

    curated_sentences = []
    for sentence in clean_sentences:
        if re.search("\[[^\]]+\]|⸤[^⸥]+⸥", sentence):
            curated_sentences.append(sentence)
    return curated_sentences


def remove_non_greek(sentences, full, punctuation_marks, noisy_pattern):
    """
    Removing all non Greek characters from a set of sentences.
    """
    greek_sentences = []
    non_greek_sentences = []

    for sentence in sentences:

        # ---- Removing noisy blocks --- #
        clean_sentence = regex.sub(noisy_pattern, ' ', sentence)
        clean_sentence = regex.sub("(\s){2,}", ' ', clean_sentence)

        # ---- Removing non Greek characters --- #
        if full:
            if punctuation_marks == "yes":
                clean_sentence = regex.sub(
                    "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s,;·]", '', clean_sentence)
            else:
                clean_sentence = regex.sub(
                    "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s]", '', clean_sentence)
        else:
            if punctuation_marks == "yes":
                clean_sentence = regex.sub(
                    "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s,;·\[\]⸤⸥]", '', clean_sentence)
            else:
                clean_sentence = regex.sub(
                    "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s\[\]⸤⸥]", '', clean_sentence)

        clean_sentence = regex.sub("(\s){2,}", ' ', clean_sentence)

        num_of_words = len(regex.findall("[\p{L}\p{M}*]+", clean_sentence))

        if num_of_words >= 2:  # Only sentences with two or more words
            greek_sentences.append(clean_sentence)
            non_greek_sentences.append(sentence)

    return non_greek_sentences, greek_sentences


def report_excluded_files(root: str, corpus_path: str, not_included_files: list):

    file_path = root + "not_included/" + "not_included.txt"
    file = open(
        file_path, 'w', encoding="utf8")

    to_report = '\n'.join(s for s in not_included_files)

    file.write(''.join(to_report))

    file.close()

    for file_ in not_included_files:

        # Construct the full file paths
        src_path = os.path.join(corpus_path, file_)
        dst_path = os.path.join(root + "not_included/", file_)
        # Copy the file
        shutil.copy(src_path, dst_path)


def debugger(files, argv):
    """
    Building the sets of clean and noisy sentences contained in the corpus
    """
    # An argument defining that some punctuation marks must be kept (,;·)
    name = argv.split("=")[0]
    value = argv.split("=")[1]
    if name == "--punctuation_marks" and (value == "yes" or value == "no"):
        punctuation_marks = value
    else:
        print("Please be sure about the argument syntax : \
               --punctuation_marks=<yes>|<no>")
        exit()

    corpus_file = {}
    corpus = []
    not_included_files = []
    # noisy_pattern = "(\.\s){2,}|(\.){2,}|(—\s){2,}|(-\s){2,}|\[\s+\]|[¯˘⏓\-⏑]+|(\s—){2,}|(\s-){2,}|\!{1,}|—+"
    noisy_pattern = "(\.\s){2,}|(\.){2,}|(—\s){2,}|(–\s){2,}|(-\s){2,}|(⸐\s){2,}|(\s+){2,}|[¯˘⏓\-—–⸐⏑\?]+|(\s—){2,}|(\s–){2,}|(\s-){2,}|(\s⸐){2,}|\!{1,}|\¡{1,}"

    processed_files = 0

    for file in files:
        processed_files += 1
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()
        file_name = file.split("/")[-1]
        corpus_file["name"] = file_name
        clean_sentences = []
        noisy_sentences = []

        print("Processing corpus file {}: {}/{}".format(file_name,
              processed_files, len(files)), "\n")

        # Building the sets of clean and noisy sentences
        # for a set of lines (a file) #
        all_lines = ''
        for line in lines:

            if not line == "\n":
                line = line.replace("\n", "").strip()

                if line.endswith('-'):
                    all_lines += line.strip('-')
                else:
                    all_lines += line + " "

        # Removing {} and () metadata blocks
        all_lines = regex.sub(
            r'[{\(][\(\)<>〈〉,\s—\.\-\d;\p{L}]+[\)}]', '', all_lines).strip()
        # Removing ASCII letters and numbers
        all_lines = regex.sub(r'[a-zA-Z0-9]+', '', all_lines)

        # print(all_lines)

        noisy_blocks = []

        noisy_block_matches = re.finditer(noisy_pattern, all_lines)

        if noisy_block_matches:
            for block in noisy_block_matches:
                noisy_blocks.append(block)

        length_noisy_blocks = len(noisy_blocks)

        if not noisy_blocks:
            line_sentences = []
            line_sentences = re.split('\.', all_lines)
            for sentence in line_sentences:
                if not sentence.isspace():
                    clean_sentences.append(sentence)

        else:  # For a set of lines (a file) with at least a noisy block

            current_coordinate = 0
            block = 0

            while block < length_noisy_blocks - 1:

                start_noisy_block = noisy_blocks[block].start()
                before_start_block = all_lines[current_coordinate:start_noisy_block]

                # Getting the end noisy block for the noisy sentence in
                #  progress and the next noisy block ahead
                next_block, end_block = get_end_noisy_block(
                    all_lines, noisy_blocks, block, noisy_pattern)

                end_noisy_block = end_block.end()

                if next_block < len(noisy_blocks) - 1:
                    after_end_block = all_lines[end_noisy_block:noisy_blocks[next_block].start(
                    )]
                else:
                    after_end_block = all_lines[end_noisy_block:]

                before_start_block_sentences = re.split(
                    '\.', before_start_block)
                after_end_block_sentences = re.split('\.', after_end_block)

                noisy_sentence = before_start_block_sentences[-1] + \
                    all_lines[start_noisy_block:end_noisy_block] + \
                    after_end_block_sentences[0]

                if block == 0:

                    current_coordinate += end_noisy_block + \
                        len(after_end_block_sentences[0]) + 1
                    del before_start_block_sentences[-1]

                    clean_sentences.append(noisy_sentence)

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
                    clean_sentences.append(noisy_sentence)

                block = next_block

            else:  # Processing the last noisy block
                end_noisy_block = noisy_blocks[block].end()
                after_end_block = all_lines[end_noisy_block:]
                after_end_block_sentences = re.split('\.', after_end_block)

                if current_coordinate < end_noisy_block:
                    start_noisy_block = noisy_blocks[block].start()
                    before_start_block = all_lines[current_coordinate:start_noisy_block]
                    before_start_block_sentences = re.split(
                        '\.', before_start_block)

                    noisy_sentence = before_start_block_sentences[-1] + \
                        all_lines[start_noisy_block:end_noisy_block] + \
                        after_end_block_sentences[0]
                    clean_sentences.append(noisy_sentence)

                    if len(before_start_block_sentences) > 1:
                        del before_start_block_sentences[-1]
                        for sentence in before_start_block_sentences:
                            if not sentence.isspace():
                                clean_sentences.append(sentence)

                if len(after_end_block_sentences) > 1:
                    del after_end_block_sentences[0]
                    # print(len(after_end_block_sentences))
                    for sentence in after_end_block_sentences:
                        if not sentence.isspace():
                            clean_sentences.append(sentence)

        # removing all non greek characters from the clean sentences set
        noisy_sentences, clean_sentences = remove_non_greek(
            clean_sentences, True, punctuation_marks, noisy_pattern)

        # Setting a new processed corpus file
        corpus_file["clean"] = clean_sentences
        corpus_file["noisy"] = noisy_sentences

        len_sentences = len(clean_sentences)

        if len_sentences >= 1:  # Only processed files with one or more
                                # sentences go to the corpus.
            if len_sentences == 1:
                num_of_words = len(regex.findall(
                    "[\p{L}\p{M}*]+", clean_sentences[0]))
                if num_of_words > 2:
                    # Updating the processed corpus with a new processed file
                    corpus.append(copy.deepcopy(corpus_file))
            else:
                # Updating the processed corpus with a new processed file
                corpus.append(copy.deepcopy(corpus_file))

        else:
            not_included_files.append(file_name)

        corpus_file.clear()

    return (corpus, not_included_files)


def report_sentences(file, path):
    """
    reporting a set of sentences
    """
    file_to_report = open(
        path, 'w', encoding="utf8")

    clean = file["clean"]
    noisy = file["noisy"]

    for item in range(len(clean)):
        file_to_report.write("\n" + "=====:" + "\n")
        file_to_report.write("\n" + "before:" + "\n")
        file_to_report.write(noisy[item].strip() + "." + "\n")
        file_to_report.write("\n" + "after:" + "\n")
        file_to_report.write(clean[item].strip() + "." + "\n")

    file_to_report.close()


def report_rejected(rejected, path):
    """
    Reporting the rejected files
    """
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


def report_noise(corpus, path):
    """
    Reporting the noise related to each file in the corpus
    """
    noise_rate_file = "/noise_rate.txt"
    noise_index_file = "/noise_index.txt"
    file_path = path + noise_index_file

    # Sorting the corpus in descending order based on the index of noise
    corpus.sort(key=lambda x: x["noise_index"], reverse=True)

    print("Reporting the corpus' files order based on the index of noise.....")
    print("\n")
    time.sleep(2)  # To see on console what is happening.
    report = open(
        file_path, 'w', encoding="utf8")
    report.write("File:" + "\t" + "\t" + "\t" + "\t" +
                 "Noise rate:" + "\t" + "Noise index:" + "\n")

    for file in corpus:
        report.write(file["name"] + "\t" + "\t" + str(file["noise_rate"]
                                                      ) + "\t" + "\t" + str(file["noise_index"]))
        print("\n")
    report.close()
    print("....... done" + "\n")
    time.sleep(2)

    # Sorting the corpus in descending order based on the noise rate
    corpus.sort(key=lambda x: x["noise_rate"], reverse=True)

    file_path = path + noise_rate_file

    print("Reporting the corpus' files order based on the rate of noise.....")
    time.sleep(2)
    report = open(
        file_path, 'w', encoding="utf8")
    report.write("File:" + "\t" + "\t" + "\t" + "\t" +
                 "Noise rate:" + "\t" + "Noise index:" + "\n")
    for file in corpus:
        report.write(file["name"] + "\t" + "\t" + str(file["noise_rate"]
                                                      ) + "\t" + "\t" + str(file["noise_index"]))
        print("\n")
    report.close()
    print("....... done" + "\n")


if __name__ == '__main__':
    """
    Debugging the corpus and reporting the related files' noise
    """

    folders = ["clean", "not_included"]

    root = "./texts/"
    corpus_path = root + "corpus"

    for folder in folders:
        _path = root + folder
        if path.exists(_path):
            shutil.rmtree(_path)
        os.mkdir(_path)

    files = [str(x) for x in Path(corpus_path).glob("**/*.txt")]

    # Debugging the corpus and measuring the related files' noise
    # Also getting the not included (yet) files

    corpus, not_included_files = debugger(files, sys.argv[1])

    # Reporting the different set of sentences and the noise measures.
    print("Saving the processed sentences ......")
    print("\n")

    time.sleep(2)  # To see on console what is happening.

    for file in corpus:

        file_name = "/" + file["name"]

        file_path = _path + file_name
        # Reporting the sets of sentences
        report_sentences(file, file_path)

    print("Reporting the excluded files ......")
    print(f'Excluded files: {len(not_included_files)} / {len(files)}')
    print("\n")

    report_excluded_files(root, corpus_path, not_included_files)

    print("....... done")
