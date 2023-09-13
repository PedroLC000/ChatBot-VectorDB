import streamlit as st
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import os
from PIL import Image

def context_condition(context_documents):
    scores = ([(context_documents[i][1]) for i in range(len(context_documents))])
    meancontext = sum(scores)/len(scores)    
    if meancontext < st.session_state['mediaContexto']:
        context = '\n\n'.join([context_documents[i][0].page_content for i in range(len(context_documents))]) 
    else:
        context = ''
    return context

def prompt_rules():
    prompt = """
    Você é uma assistente virtual que auxilia usuários com dúvidas. Siga essas regras:
        - Seja breve, responda a dúvida do usuário e nada mais. 
        - Responda SOMENTE com base nos fatos listados nos Textos Fornecidos e nas mensagens anteriores. 
        - Se não houver informações nos Textos Fornecidos ou nas mensagens anteriores, diga que não sabe a resposta para a dúvida do usuário. 
        - Caso necessário peça para o usuário para refazer a pergunta de outra maneira, ou para entrar em contato com o suporte.
    """
    return prompt

def constructor_prompt(context, query):
    promtpContQuery = """
    \nTextos Fornecidos: [{context}]
    \nPergunta: [{query}]
    """.format(query=query, context=context)
    return promtpContQuery

def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def initialize_session_state():
    if 'nameChatBot' not in st.session_state:
        st.session_state['nameChatBot'] = 'CBot'

    if 'messages' not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": f"Olá! Sou o {st.session_state['nameChatBot']}, como posso te ajudar?"}]

    if 'history' not in st.session_state:
        st.session_state['history'] = [{'role': 'system', 'content': prompt_rules()}]

    if 'tamHistoricoMensagens' not in st.session_state:
        st.session_state['tamHistoricoMensagens'] = 3
    
    if 'tamBuscaSimilaridade' not in st.session_state:
        st.session_state['tamBuscaSimilaridade'] = 3

    if 'mediaContexto' not in st.session_state:
        st.session_state['mediaContexto'] = 0.4

    if 'tamQuery' not in st.session_state:
        st.session_state['tamQuery'] = 256

    if 'tempChat' not in st.session_state:
        st.session_state['tempChat'] = 0.3

def load_openai_key():
    with open("./openai_api_key", "r") as openai_key_file:
        os.environ['OPENAI_API_KEY'] = openai_key_file.read().strip()

    openai.api_key_path = "./openai_api_key"

def history_messages(query, response):
    st.session_state['history'].append({'role': 'user', 'content': query})
    st.session_state['history'].append({'role': 'assistant', 'content': response})
    if(st.session_state['tamHistoricoMensagens'] > 0):
        st.session_state['history'] = st.session_state['history'][:1]+st.session_state['history'][-(st.session_state['tamHistoricoMensagens']*2):]
    else:
        st.session_state['history'] = []
        st.session_state['history'] = [{'role': 'system', 'content': prompt_rules()}]
def moderation_messages(query):
    response = openai.Moderation.create(input=query)
    output = response["results"][0]['flagged']
    return output

def generate_response(query):
    if len(query) <= st.session_state['tamQuery'] and moderation_messages(query) == False:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        store2 = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        context_documents = store2.similarity_search_with_score(query=query, k=st.session_state['tamBuscaSimilaridade'], search_type="similarity")
        context = context_condition(context_documents)
        prompt = constructor_prompt(context, query)
        st.session_state['history'].append({'role': 'user', 'content': prompt})
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state['history'],
                temperature=st.session_state['tempChat']
            )   
        st.session_state['history'].pop(-1)
        print('\n################################################################\n')
        print(prompt)
        print('Resposta: ', response['choices'][0]['message']['content'])
        print('\nHistórico Mensagens: ', st.session_state['history'])
        print('\nTokens: \n', response['usage'])
        response = response['choices'][0]['message']['content']
        history_messages(query, response)
    else:
        response = '''Infelizmente não posso responder essa pergunta pois ela excede os 
        limites de caracteres ou inflige as políticas da empresa.
        '''
    return response

def message():
    if prompt := st.chat_input(placeholder="Faça sua pergunta aqui"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Um momento..."):
                response = generate_response(prompt) 
                st.write(response) 
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

def sidebar_parametros():
    st.sidebar.title('Configurações: ')
    st.session_state['tamHistoricoMensagens'] = st.sidebar.slider('Histórico de Mensagens', 0, 3, 3, help='Tamanho de mensagens que o bot lembrará')
    st.session_state['tamBuscaSimilaridade'] = st.sidebar.slider('Busca Similaridade', 1, 3, 3, help='Quanto menor menos inforções o prompt vai ter para elaborar um resposta para o usuário')
    st.session_state['mediaContexto'] = st.sidebar.slider('Media Score Contexto', 0.0, 1.0, 0.4, 0.1, help='Quanto menor mais especificos são os textos que serão pesquisados com o input do usuário')
    st.session_state['tamQuery'] = st.sidebar.slider('Caracteres Máximo Input', 0, 500, 256, help='Número de caracteres máximo para a pergunta do usuário')
    st.session_state['tempChat'] = st.sidebar.slider('Temperatura Chat', 0.0, 1.0, 0.3, 0.1, help='Quanto menor mais sem criativade o bot é para elaborar a resposta, já quanto maior mais criativo')

if __name__ == "__main__":

    initialize_session_state()
    st.set_page_config(page_title=st.session_state['nameChatBot'], 
                       page_icon=Image.open("icons\\icon_unilab_branco.png"), 
                       layout='centered', 
                       initial_sidebar_state='collapsed', 
                       menu_items=None)
    st.title(st.session_state['nameChatBot'])
    load_openai_key()
    sidebar_parametros()
    display_messages()
    message()
    
