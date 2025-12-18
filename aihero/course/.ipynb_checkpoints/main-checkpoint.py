import io
import zipfile
import requests
import frontmatter

def main():
    print("Hello from course!")
    url = 'https://codeload.github.com/DataTalksClub/faq/zip/refs/heads/main'
    resp = requests.get(url)
    repository_data = []

    # Create a ZipFile object from the downloaded content
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    for file_info in zf.infolist():
        filename = file_info.filename.lower()
    
        # Only process markdown files
        if not filename.endswith('.md'):
            continue
    
        # Read and parse each file
        with zf.open(file_info) as f_in:
            content = f_in.read()
            post = frontmatter.loads(content)
            data = post.to_dict()
            data['filename'] = filename
            repository_data.append(data)
    
    zf.close()
    print(repository_data[1])


if __name__ == "__main__":
    main()
