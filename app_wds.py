import streamlit as st
import pandas as pd
import json
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from funcsupport import truncate_passage, postprocess_results
from dotenv import load_dotenv
import os

from SessionState import get



session_state = get(password='')



# load_dotenv('.env')

def main():

  APIKEY = os.getenv("APIKEY")
  URL = os.getenv("URL")
  VERSION = os.getenv("VERSION")


  st.title("QnA functionality")


  #authenticator
  authenticator = IAMAuthenticator(APIKEY)
  discovery = DiscoveryV2(
      version=VERSION,
      authenticator=authenticator
  )

  discovery.set_service_url(URL)

  def query_with_answer(question_in_answer,proj_id,sel_col):
      response = discovery.query(
        project_id = proj_id,
          collection_ids = [sel_col],
          count = 20,
        natural_language_query = question_in_answer,
          passages={"enabled":True, "count":10, "find_answers":True, "per_document":True, "characters":9900, "max_answers_per_passage": 3},

          aggregation = None,

          return_ = ['document_passages.answers']

      ).get_result()
      return response

  def get_the_doc_name (docid,proj_id,sel_col):
    '''Queries WDS and returns the doc id'''
    q_string = "document_id:"+str(docid)
#     print(q_string)
    response = discovery.query(
        project_id = proj_id,
        collection_ids = [sel_col],
        count = 1,
        query = q_string,
#         passages={"enabled":True, "count":20, "find_answers":True, "per_document":True, "characters":5000, "max_answers_per_passage": 2},
#         aggregation = None,
        return_ = ['metadata']
        ).get_result()
    return (response['results'][0]['metadata'][0]['dataroom_relative_path'])

  
  project_list = discovery.list_projects().get_result()['projects']
  df_projects = pd.json_normalize(project_list)
  df_projects_sel = df_projects[['name']]

  choose_project = st.sidebar.selectbox('choose project',(df_projects_sel), index= 3)

  proj_id = df_projects[df_projects['name']==choose_project]['project_id'].iloc[0]

  collection_list = discovery.list_collections(
    project_id=proj_id).get_result()['collections']

  df_collections = pd.json_normalize(collection_list)

  if len(df_collections)>1:
      sel_col_in = st.sidebar.selectbox('choose collections',(df_collections['name']))
      sel_col = df_collections[df_collections['name']==sel_col_in]['collection_id'].iloc[0]
  else:
      sel_col = df_collections['collection_id'].iloc[0]

  input_sent = st.text_input("Input Question", "Your question goes here")

  # st.write(input_sent)

  if st.button('query'):
      response_out = query_with_answer(input_sent,proj_id,sel_col)
      st.write("*total number of docs*")
      st.write(response_out['matching_results'])
      # for num_resp in range(min(len(response_out['results'])-1,5)):
      #     st.write(response_out['results'][num_resp]["document_passages"][0]['answers'][0]['answer_text'])
      
      df_answers = pd.json_normalize(response_out['results'])
      df_answers_2 = postprocess_results(df_answers)
      co_name = df_answers_2['answer_1']
      st.sidebar.table(co_name)
      for index, row in df_answers_2.iterrows():
          # st.write(f'**answer {index}: **')
          st.markdown(f'answer: **{row.answer_1}** with confidence {str(row.answer_1_confidence)[0:5]}')
          filepath_doc = get_the_doc_name (row.document_id,proj_id,sel_col)
          st.markdown(filepath_doc)
          # st.write('*alternative answers same passage*')
          # st.write(row.answer_2, row.answer_3)
          # st.write(row.answer_3)
          st.write('short passage with higlight')
          st.markdown(row.truncated_passage, unsafe_allow_html=True )
          st.write('long passage with higlight')
          st.markdown(row.passage_text, unsafe_allow_html=True )
          st.write('-----------')

          # st.write(df_answers_2[['answer_1','truncated_passage','passage_text']])
      








  # def return_NER(value):
  #     doc = nlp(value)
  #     return [(X.text, X.label_) for X in doc.ents]

  # # Add title on the page
  # st.title("Spacy - Named Entity Recognition")

  # # Ask user for input text
  # input_sent = st.text_input("Input Sentence", "Your input sentence goes here")

  # # Display named entities
  # for res in return_NER(input_sent):
  #     st.write(res[0], "-->", res[1])

if session_state.password != 'W@ts0n':
    pwd_placeholder = st.sidebar.empty()
    pwd = pwd_placeholder.text_input("Password:", value="", type="password")
    session_state.password = pwd
    if session_state.password == 'W@ts0n':
        pwd_placeholder.empty()
        main()

    else:
        st.error("The password you entered is incorrect")
else:
    main()