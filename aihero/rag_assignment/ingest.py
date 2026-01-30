import io
import requests
import zipfile
from minsearch import Index
#import frontmatter
import requests
import PyPDF2
from io import BytesIO
import logging
logging.basicConfig(level=logging.DEBUG)

def sliding_window(seq, size, step):
    if (size<=0 or step<=0):
        raise ValueError("size/step must be positive")
    n=len(seq)
    result =[]
    for i in range(0,n,step):
        batch = seq[i:i+size]
        result.append({'start':i,'content':batch})
        if(i+size >= n):   
            break
    return result

def chunk_documents(docs, size=2000, step=1000):
    chunks = []
    for doc in docs:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content')
        doc_chunks = sliding_window(doc_content, size=size, step=step)
        for chunk in doc_chunks:
            chunk_copy = chunk.copy()
            chunk_copy.update(doc_copy)
            chunks.append(chunk_copy)
    return chunks

def index_data(url_path,filter =None,chunk= True,chunking_params=None):
    docs =read_repo_data(url_path)
    if filter is not None:
        docs = [doc for doc in docs if filter(doc)]
    if chunk:
        if chunking_params is None:
            chunking_params = {'size':2000,'step':1000}
        docs=chunk_documents(docs,**chunking_params)
    index=Index(
        text_fields=["content","filename"]
    )
    index.fit(docs)
    return index

def read_repo_data(url_path):
    #url_path = 'https://www.cms.gov/files/document/draft-oasis-e1-manual-04-28-2024.pdf'
    resp = requests.get(url_path, stream=True)
    
    # Extract filename from URL
    filename_repo = url_path.split('/')[-1]  
    repository_data = []
    # Read PDF content
    pdf_file = BytesIO(resp.content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Extract text from all pages
    text_content = ''
    for page in pdf_reader.pages:
        text_content += page.extract_text()
    
    # Create a dictionary with the structure expected by chunk_documents
    data = {
        'content': text_content,
        'filename': filename_repo
    }
    print("Data is ",data)
    repository_data.append(data)
    return repository_data




