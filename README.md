# ChatBot-VectorDB

> A ideia é implementar um ChatBot personalizado baseado em busca com o uso do Chroma e OpenAI Embeddings.

## 🚀 Execução

Primeiro é necessário criar e alimenta o Vector DataBase Chroma com os Embeddings dos dados de entrada, podendo ser arquivos .txt ou .pdf

```
streamlit run loader.py
```

Com o Vector DataBase criado é possível iniciar o ChatBot personalizado

```
streamlit run index.py
```
