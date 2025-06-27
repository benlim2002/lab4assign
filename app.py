import streamlit as st
from pymongo import MongoClient
import requests

# MongoDB Setup
uri = "mongodb+srv://benLab4:benlab4ass@cluster0.goopkpm.mongodb.net/"
client = MongoClient(uri)
db = client["imported"]
collection = db["uniprot_proteins"]

# Embedding Function
def ollama_embed(text):
    url = 'http://localhost:11434/api/embeddings'
    model = 'nomic-embed-text'
    response = requests.post(url, json={"model": model, "prompt": text})
    return response.json()['embedding']

#search function
def search_vector(query, limit=5):
    query_embedding = ollama_embed(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "prot_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": min(limit * 10, 1000),
                "limit": limit
            }
        },
        {
            "$project": {
                "uniprot_id": 1,
                "protein_name": 1,
                "organism": 1,
                "sequence_length": 1,
                "function": 1,
                "go_molecular_function": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

#ui
st.title("🧬 Protein Search using MongoDB Vector Embeddings")
query = st.text_input("Enter a query (e.g., 'protein for Homo sapiens with DNA binding')")

if st.button("Search"):
    if query:
        results = search_vector(query)
        st.write(f"Top {len(results)} Results:")
        for res in results:
            st.markdown("---")
            st.markdown(f"**Protein Name:** {res['protein_name']}")
            st.markdown(f"**Organism:** {res['organism']}")
            st.markdown(f"**Function:** {res['function']}")
            st.markdown(f"**GO Function:** {res['go_molecular_function']}")
            st.markdown(f"**Sequence Length:** {res['sequence_length']}")
            st.markdown(f"**Score:** {round(res['score'], 4)}")
    else:
        st.warning("Please enter a search query.")
