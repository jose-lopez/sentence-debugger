# -*- coding: utf-8 -*-

'''
Created on 21 Nov. 2023
@author: jose-lopez
'''

import copy
from os import path
import os
from pathlib import Path
import shutil
import time

import regex


def remove_non_greek(file: str, noisy_pattern: str) -> list:
    """
    Removing all non Greek characters from a set of sentences.
    """
    greek_sentences = []

    # ---- Removing noisy blocks --- #
    clean_file = regex.sub(noisy_pattern, ' ', file)

    # ---- Removing non Greek characters --- #
    clean_file = regex.sub(
        "[^\u1F00-\u1FFF\u0370-\u03FF\.'\s]", '', clean_file)

    clean_file = regex.sub("(\s){2,}", ' ', clean_file)

    clean_sentences = clean_file.split(".")

    len_clean_sentences = len(clean_sentences)

    # If a processed file has one or more sentences
    if len_clean_sentences >= 1:
        greek_sentences = clean_sentences

    """
    if len_clean_sentences >= 1:  # Only processed files with one or more sentences
        if len_clean_sentences == 1:
            num_of_words = len(regex.findall(
                "[\p{L}\p{M}*]+", clean_sentences[0]))
            if num_of_words > 2:
                greek_sentences = clean_sentences
        else:
            greek_sentences = clean_sentences
    """

    return greek_sentences


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


def debugger(files):
    """
    Building the sets of clean and noisy sentences contained in the corpus
    """

    corpus_file = {}
    corpus = []
    not_included_files = []

    noisy_pattern = "(\.\s){2,}|(\.){2,}|(—\s){2,}|(–\s){2,}|(-\s){2,}|(⸐\s){2,}|(\s+){2,}|[¯˘⏓\-—–⸐⏑\?]+|(\s—){2,}|(\s–){2,}|(\s-){2,}|(\s⸐){2,}|\!{1,}|\¡{1,}"

    processed_files = 0

    for file in files:
        processed_files += 1
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()
        file_name = file.split("/")[-1]
        corpus_file["name"] = file_name
        clean_sentences = []

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

        # removing all non greek characters from the file
        clean_sentences = remove_non_greek(
            all_lines, noisy_pattern)

        # Setting a new processed corpus file
        corpus_file["clean"] = clean_sentences

        len_sentences = len(clean_sentences)

        # Updating the processed corpus with a new processed file
        if not len_sentences == 0:
            corpus.append(copy.deepcopy(corpus_file))
        else:
            not_included_files.append(file_name)

        corpus_file.clear()

    return corpus, not_included_files


def report_sentences(file, path):
    """
    reporting a set of sentences
    """
    file_to_report = open(
        path, 'w', encoding="utf8")

    clean_sentences = file["clean"]

    for sentence in clean_sentences:
        if not sentence == '':
            file_to_report.write(sentence.strip() + "." + "\n" + "\n")

    file_to_report.close()


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

    # Getting the clean corpus and reporting the not included files
    corpus, not_included_files = debugger(files)

    # Reporting the different set of sentences and the noise measures.
    print("Saving the processed sentences ......")
    print("\n")

    time.sleep(2)  # To see on console what is happening.

    for file in corpus:

        file_name = "/" + file["name"]
        file_path = root + "clean/" + file_name
        # Reporting the sets of sentences
        report_sentences(file, file_path)

    print("Reporting the excluded files ......")
    print(f'Excluded files: {len(not_included_files)} / {len(files)}')
    print("\n")

    report_excluded_files(root, corpus_path, not_included_files)

    print("....... done")
