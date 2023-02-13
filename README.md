# Master's Thesis on Subject-Verb-Object (SVO) Extraction in English, French, Spanish, Italian and German

## 1. Description

This repository contains an extractor used to extract morpho-syntactic patterns for semantic information retrieval. The extractor was applied on newspaper articles.

Franzosi proposes that narrative texts - that is, newspaper articles - are characterized
by a sequence of events in which there is an actor (primarily human) who does
certain things in relation to other actors. This so-called actor-action-actor structure
corresponds linguistically to a subject, i.e. the first actor, a temporally contextualized
verb, i.e. the action, and a syntactic complement or object, i.e. the second actor (Franzosi, 2010).

My work focuses on obtaining the information that an actor performs a certain action
in relation to a second actor or object, relying on the idea of SVO triplets 
as a narrative unit proposed by Franzosi. However, languages have more complex
ways of expressing that someone does something in relation to someone or something else; 
SVO triplets are a simplification. As part of this work, I examined newspaper articles 
and pick out all possible patterns that could express this information. In a second step, 
I examined which patterns can be extracted with spaCy's Dependency Matcher.

## 2. Usage

In order to get the SVO triplets from a text, the following input is required with the obligatory arguments input file (txt file) and a language (en, fr, es, it, de): 

    python main.py input_file.txt language


An example is the following:

    python main.py international_womens_day.txt en

The output contains a dictionary with the name of the pattern and the indexes of the subject, verb and object in the text. 
    
    {'pattern_name': 'SVO', 'S': 2, 'V': 3, 'O': 5}
    {'pattern_name': 'SVO', 'S': 19, 'V': 20, 'O': 22}
    
Additionally, a compressed jsonl file is created with further information about the text. Each line represents one newspaper article containing the extracted SVO triplets. Here an example of an output of the sentence *Turkish civil society faces a climate of repression under President Recep Tayyip Erdoğan’s conservative government* :

    {"svo_triplets": [{"pattern_name": "SVO", "S": 2, "V": 3, "O": 5, "S_token": "society", "S_lemma": "society", "S_pos": "NOUN", "V_token": "faces", "V_lemma": "face", "V_pos": "VERB", "O_token": "climate", "O_lemma": "climate", "O_pos": "NOUN"}], "meta_data": [], "legth_text": 17, "nr_verbs": 1, "unique_triplets": ["society_face_climate"], "nr_unique_triplets": 1}
    
Note that meta_data is only filled out when applied on the dataframe from Nexis DataLab.

To decompress the jsonl file, use this command:

    bzip2 -d file_name.jsonl.bz2


Additional arguments can be used:

- input format: either an individual text (indtxt) or a dataframe (datafr), default is individual text

      --input_format datafr
    
- spaCy language pipeline size: either small (sm) or medium (md), default is small

      --pipeline md
      
- unique triplets: if present, prints the unique lemmas of all the triplets found in the text

      --unique_triplets
      
- number of unique triplets: if presents, prints the number of unique triplets found in the text

      --nr_unique_triplets
      
- print: if present, prints the svo dictionary to the std output

      --print, -p
     
- output file: name of the output file, default is "svo_triplets_output.jsonl.bz2"

      --output_file filename



## 3. Data

## 4. Background

My master’s thesis is related to the postdoctoral project of Dr. Elena Fernández
Fernández. Her project quantifies Reinhart Koselleck’s theory (The Practice of
Conceptual History, 2002), which states that there is a direct relationship between
technological progress and an acceleration of the social construct of time. The social
construct of time refers to artificial units of time such as hours, minutes, and seconds
as opposed to natural time frames such as day, night, seasons, and year. This theory
assumes that as technology advances, it is possible to parse time into smaller and
smaller segments. As a result, technological progress has also made it possible to
do more things in a given amount of time. This ever-increasing productivity gives
the sensation of acceleration.

Another assumption made in this project is that the press reflects human activity.
The more things happen, the more is reported in the press. In this master’s thesis
I engage with existing work by Dr. Elena Fernández Fernández developed during
her Eurotech Post-Doctoral Grant, in which she analyses the acceleration of the
social construction of time by measuring the information density of narrative units
in the press within thirty years. The narrative units, as proposed in Franzosi’s
Quantitative Narrative Analysis (Franzosi, 2010), are the SVO triplets. The SVO triplets are thus
counted to calculate the information density, the ratio of different narrative units
per number of words per year, as the number of unique SVO triplets normalised by
the sum of words. If the number of unique normalised SVO triplet increases over
the years, it means that more narratives are published in the press, reflecting an
increment of human activities (Fernández et al., 2020).

The goal of this project is to investigate geographically information behaviour
as a result of processes of globalisation in the Western world by analysing social
acceleration in newspapers.

## 5. Reference

E. F. Fernández, M. Schoenfeld, and J. Pfeffer. Measuring the acceleration of the
social construction of time using the BOE (Boletín Oficial del Estado). In CHR
2020: Workshop on Computational Humanities Research, Amsterdam, The
Netherlands, Nov 2020. URL https://ceur-ws.org/Vol-2723/.

R. Franzosi. Quantitative Narrative Analysis. Sage, 2010.
