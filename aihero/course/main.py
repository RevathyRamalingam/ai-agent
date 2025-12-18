import io
import zipfile
import requests
import frontmatter
from minsearch import Index
from sentence_transformers import SentenceTransformer

def main():
    
    def read_repo_data(repo_owner, repo_name):
        
        prefix = 'https://codeload.github.com' 
        url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main'
        resp = requests.get(url)
        
        if resp.status_code != 200:
            raise Exception(f"Failed to download repository: {resp.status_code}")

        resp = requests.get(url)
        repository_data = []

        # Create a ZipFile object from the downloaded content
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        
        for file_info in zf.infolist():
            filename = file_info.filename.lower()
        
            # Only process markdown files
            if not filename.endswith('.md') or filename.endswith('.mdx'):
                continue
        
            # Read and parse each file
            with zf.open(file_info) as f_in:
                content = f_in.read()
                post = frontmatter.loads(content)
                data = post.to_dict()
                data['filename'] = filename
                repository_data.append(data)
        
        zf.close()
        #print("repository_data",repository_data[0])
        return repository_data
    def sliding_window(seq,size,step):
        if step<=0 or size<=0:
            raise ValueError("Negative values are not allowed")
        
        n=len(seq)
        result = []
        for i in range(0,n,step):
            chunk=seq[i:i+size]
            result.append({'start':i,'chunk':chunk})
            if(i+size>=n):
                break
        return result
    #dtfaq=read_repo_data('DataTalksClub','faq')
    dtc_faq =read_repo_data('datatalksclub','faq')
    print("dtc_faq",dtc_faq[0])
    evidently_chunks =[]
    for doc in dtc_faq:
        doc_copy=doc.copy()
        doc_content=doc_copy.pop('content')
        chunks =sliding_window(doc_content,2000,1000)
        for chunk in chunks:
            chunk.update(doc_copy)
        evidently_chunks.extend(chunks)
    #print(f"Loaded {len(dtfaq)} FAQ documents from DataTalksClub/faq")
    #print(evidently_chunks)
    index = Index(text_fields=["chunk", "title", "description", "filename"],keyword_fields=[])
    index.fit(evidently_chunks)
    query = 'When will the course be over?'
    #results = index.search(query)
    #print("\nResults:",results)
    def text_search(query):
        return index.search(query,num_results=5)

import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')

text_search_tool = {
    "type": "function",
    "name": "text_search",
    "description": "Search the FAQ database",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query text to look up in the course FAQ."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}


client = openai.OpenAI()

system_prompt = """
You are a helpful assistant for a course. 
"""

question = "I just discovered the course, can I join now?"

chat_messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question}
]



completion = client.responses.create(
    model="gpt-4o-mini",
    input=chat_messages,
    tools=[text_search_tool]
)

#print(completion.output)


if __name__ == "__main__":
    main()
