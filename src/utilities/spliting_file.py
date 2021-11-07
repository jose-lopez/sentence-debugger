# -*- coding: utf-8 -*-

import os
from datasets import load_dataset
from transformers import RobertaConfig
from transformers import RobertaTokenizer
from transformers import RobertaForMaskedLM
from pathlib import Path
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import setuptools
from transformers import LineByLineTextDataset

'''
Created on 22 oct. 2021

@author: jose-lopez
'''

if __name__ == '__main__':
    
    # file = "texts/clean/evaluation.txt"
    file = "texts/clean/oscar.eo.txt"
    # file = "texts/corpus/TLG0001.TXT-001.txt"
    lm_data_dir = "texts/clean/"
    
    with open(file, 'r', encoding="utf8") as f:
        lines = f.readlines()    
        
    train_split = 0.97
    train_data_size = int(len(lines)*train_split)
    
    with open(os.path.join(lm_data_dir,'train.txt') , 'w') as f:
        for item in lines[:train_data_size]:
            f.write(item)
    
    with open(os.path.join(lm_data_dir,'eval.txt') , 'w') as f:
        for item in lines[train_data_size:]:
            f.write(item)
            
    def tokenize_function(example):
        return tokenizer(example["text"], max_length=512, truncation=True)
    
    config = RobertaConfig(
     vocab_size=52_000,
     max_position_embeddings=512,
     num_attention_heads=12,
     num_hidden_layers=12,
     type_vocab_size=1,
    )
    
    tokenizer = RobertaTokenizer.from_pretrained('./dioBERTo/model/', max_length=512,  truncation=True)
    
    model = RobertaForMaskedLM(config=config)
    
    train_path="./dioBERTo/text/train"
    validation_path="./dioBERTo/text/validation"
    test_path="./dioBERTo/text/test"   

    
    weigths_dir = './dioBERTo/model/weights'
    if not os.path.exists(weigths_dir):
        os.makedirs(weigths_dir)
    
    train = LineByLineTextDataset(
        tokenizer=tokenizer,
        file_path=train_path + "/train.txt",
        block_size=128,
    )
    
    validation = LineByLineTextDataset(
        tokenizer=tokenizer,
        file_path=validation_path + "/eval.txt",
        block_size=128,
    )
    
    
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True, mlm_probability=0.15)
    
    training_args = TrainingArguments(
     output_dir='./dioBERTo/model/weights',
     overwrite_output_dir=True,
     num_train_epochs=1,
     per_device_train_batch_size=8,
     per_device_eval_batch_size=8,
     save_steps=10_000,
     save_total_limit=2,
     evaluation_strategy='steps' 
    )
    
    trainer = Trainer(
        model,
        training_args,
        train_dataset=train,
        eval_dataset= validation,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
        
    os.environ["CUDA_LAUNCH_BLOCKING"]='1'  #Makes for easier debugging (just in case)

    trainer.train()                   