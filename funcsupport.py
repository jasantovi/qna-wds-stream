import pandas as pd
import json
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator



def truncate_passage (text, passage_offset, position, word, num_char):

    text = text.replace("<em>","")
    text = text.replace("</em>","")
    start = max(position-num_char-passage_offset,0)
    end = min(len(text),position+len(word)+num_char-passage_offset)
    new_passage = text[start: end:1]
    index = new_passage.find(word)
    output_line = new_passage[:index] + '<b>' + word + '</b>' +new_passage[(index+len(word)):]
    return output_line

def postprocess_results(df_answers):
    '''Postprocessing of the results'''
    df_answers['passage_text'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['passage_text'].iloc[0])
    df_answers['passage_start_offset'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['start_offset'].iloc[0])
    df_answers['answer_1'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['answers'].iloc[0][0]['answer_text'])
    df_answers['answer_1_confidence'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['answers'].iloc[0][0]['confidence'])
    df_answers['answer_1_start'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['answers'].iloc[0][0]['start_offset'])
    df_answers['answer_2'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['answers'].iloc[0][1]['answer_text'])
    df_answers['answer_3'] = df_answers['document_passages'].apply(lambda x : pd.json_normalize(x)['answers'].iloc[0][2]['answer_text'])
    df_answers['truncated_passage'] = df_answers.apply(lambda x: truncate_passage(x.passage_text, x.passage_start_offset, x.answer_1_start, x.answer_1, 220), axis=1)
    return df_answers