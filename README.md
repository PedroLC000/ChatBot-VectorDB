# ChatBot-VectorDB

> A ideia é implementar um ChatBot personalizado baseado em busca com o uso do Chroma e OpenAI Embeddings.

## 🛠️ Requisitos 

É necessário fornecer uma chave da API da OpenAi, para isso crie um arquivo como o nome de openai_api_key e insira a chave nesse arquivo

## 🚀 Execução

Primeiro é necessário criar e alimenta o Vector DataBase Chroma com os Embeddings dos dados de entrada, podendo ser arquivos .txt ou .pdf

```
streamlit run loader.py
```

Com o Vector DataBase criado é possível iniciar o ChatBot personalizado

```
streamlit run index.py
```
