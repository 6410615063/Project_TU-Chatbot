import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import json
import google.generativeai as genai
import torch

# Load environment variables
load_dotenv()

# Initialize Pinecone
pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Initialize BGE embedding model
device = "cuda" if torch.cuda.is_available() else "cpu"
bge_embedding = SentenceTransformer('BAAI/bge-m3', device=device)

# Initialize Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

INDEX_NAME = 'bge-json-project-rag-'
embedded_list = ["all-faculty"]

def get_response(user_prompt, system_prompt=" ", prefill=" ", temperature=0):
    try:
        response = model.generate_content(
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user_prompt,
                        }
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "text": prefill,
                        }
                    ]
                },
            ],
            generation_config={
                "temperature": temperature,
                "max_output_tokens": 8192,
            }
        )
        return response.text
    except Exception as e:
        print(f"Error in get_response: {str(e)}")
        return "Sorry, I'm having trouble generating a response right now."

def RAG_response(query):
    score = {'all-faculty': 0}
    doc_top = {'all-faculty': []}
    
    for doc in embedded_list:
        index = pinecone.Index(INDEX_NAME + doc)
        
        # Calculate query embedding
        query_embedding = bge_embedding.encode(query)
        
        # Query Pinecone
        query_results = index.query(
            namespace=INDEX_NAME + doc,
            vector=query_embedding.tolist(),
            top_k=10
        )
        
        score[doc] = query_results['matches'][0]['score']
        
        # Get document IDs and fetch metadata
        closest_doc_ids = [match['id'] for match in query_results['matches']]
        
        for doc_id in closest_doc_ids:
            doc_info = index.fetch(ids=[doc_id], namespace=INDEX_NAME + doc)
            vector_data = doc_info.vectors[doc_id]
            
            if vector_data and vector_data.metadata:
                document_text = vector_data.metadata.get('text')
                if document_text:
                    document_text = json.loads(document_text)
                    doc_top[doc].append(str(document_text))
    
    # Find best matching document
    max_score = max(score, key=score.get)
    
    # Combine relevant documents
    closest_documents = []
    if max_score in doc_top:
        closest_documents.extend(doc_top[max_score])
        document_text = "\n".join(closest_documents)
        
        # Create prompt
        prompt = f"""
        <system>
        You are a helpful assistant specializing in providing accurate, clear, and detailed explanations in Thai. Your primary task is to answer questions based on the provided relevant documents.

        Guidelines:
        1. Analyze the question carefully and refer to the document text to derive your answers.
        2. Provide responses in clear and concise Thai, maintaining accuracy and simplicity.
        3. If the document lacks sufficient information, state that clearly instead of guessing.
        </system>

        <user>
        Question: {query}
        </user>

        <documents>
        {document_text}
        </documents>

        <assistant>
        """
        
        return get_response(prompt)
    
    return "Sorry, I couldn't find relevant information to answer your question." 