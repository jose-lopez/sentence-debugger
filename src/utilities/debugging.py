'''
Created on 27 ago. 2021

@author: jose-lopez
'''
import regex
from pathlib import Path
import os
from os import path
if __name__ == '__main__':
    
    root = "./corpus_greek_test/"  
    corpus = root + "corpus"
    debugging = root + "debugging/"
    
    if not path.exists(debugging):
        os.mkdir(debugging)            
        
    files = [str(x) for x in Path(corpus).glob("**/*.txt")]
    
    for file in files:
        
        file_name = file.split("/")[-1]
        
        no_debug = open(debugging + file_name + "_no_debug", 'w', encoding="utf8")
        debug = open(debugging + file_name + "_debug", 'w', encoding="utf8")
        only_ancient = open(debugging + file_name + "_ancient", 'w', encoding="utf8")
        
        with open(file, 'r', encoding="utf8") as f:
            lines = f.readlines()
            
        # --- Building a first version of the debugged files for a corpus --- #
        all_lines = ''        
        for line in lines:
                    
            if not line == "\n":
                line = line.replace("\n", "").strip()   
                                
                if line.endswith('-'):
                    all_lines += line.strip('-')
                else:
                    all_lines += line + " "
        
        no_debug.write(all_lines)
        no_debug.close()
        
        # Removing {} and () metadata blocks
        all_lines = regex.sub(r'[{\(][〈〉,\s—\.\-\d;\p{L}]+[\)}]', '', all_lines).strip()
        
        # Removing ASCII letters and some noisy characters
        all_lines = regex.sub(r'[;a-zA-Z\(\){}]+', '', all_lines)
        
        debug.write(all_lines)
        debug.close()
        
        # Removing non Ancient Greek characters 
        # Using unicode blocks     
        # all_lines = regex.sub(r'[^\u0370–\u03FF\u1F00–\u1FFF,·\.\s\[\]]+', '', all_lines).strip() 
        # Using a character set 
        # all_lines = regex.sub(r'[^α-ωΑ-Ωἀ-Ὠἄ-ὤ\[\]]+', '', all_lines)
        # Using a list of non Greek characters
        all_lines = regex.sub(r'[⸐⸏?!\〈〉"{}⸤⸥΄|Ϛݲ§ϛ♃5ᾱᾅὝᾂ̆ᾦ#Ἦ*ᾆ⟩ὋἎὒὮ′̣ϝὯἾ͵ῂüὬ⌋⌈‚•ä+̀ö&–ͅᾕë1͂ῲᾡἇἛἋGϠ¶%ῢ^ἊἯæᾇ\\2ᾁῡἚ̋/⌉Ὢß⌊Ἣ=ῗóΌ`3ï⌞⌟ᾲΆ65ϡ̈4∗Ὣq═òΈϞ○à7áΊᾒ‖~אϟΪϥ›\u200b⁄‹íé⋖ὊÍ9Ἲ̄8{ῧ}Üᾟᾍᾨ―ΉŕὟ⩹✶0Ώᾯᾥᾌ\x8d⟦⟧\x9a¦ᾬἻ£a⋇ῐ¬ÓbῚŒἿἏÉῌᾃ\x98°ΎῈÁ⨆�ç↑ạὛ⏔⏑̅✝ú\x9dᾺụᾢᾓᾘῼùÒSῠϙ─\x90לṕᾣô\x9cῸᾜḿ$⦵⊏ī\x9eֹ\x8eÌćÆ\x8fǁ⊻@ū÷Ҁ∾ῺìῪ\x8c\x81ᾮᾈèÿœῩῊ\x88⊤З♀⊙\xadÄÖᾞߤ⁑⸨\x8aḍ⫯∼źẂ⋆★Ῑᾩ‵ᾎý√⏝⏓⏕ṃ×ȳហḾti¿⥽⥼⊣⊔ӄẉ͎\u070eҏďĎ̠◻ᾰ\ue1c2rƑ̧\x7fេឲិតាỳӕῘLᾙΫẃ☾☿♂♄⊢⋃Ā±TMĹ€║̇čō”]', '', all_lines)
        
        # Removing empty double brackets
        # all_lines = regex.sub(r'(\[\s*\])', '', all_lines)
       
        only_ancient.write(all_lines)
        only_ancient.close()
        