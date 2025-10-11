# import libraries
import os
from dotenv import load_dotenv
from openai import OpenAI
# Load environment variables

load_dotenv()  # Loads environment variables from .env
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

# A function to call an LLM model and return the response 
def call_llm_model(model, messages, temperature=1.0, top_p=1.0):    
    client = OpenAI(base_url=endpoint,api_key=token) 
    response = client.chat.completions.create(
    messages=messages,
    temperature=temperature, top_p=top_p, model=model) 
    return response.choices[0].message.content

# A function to generate note title and tags from content
def generate_note_metadata(content):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that analyzes text and generates appropriate titles and tags. Return your response in the format: 'Title: <title>\nTags: <tag1>, <tag2>, <tag3>'"},
        {"role": "user", "content": f"Generate a title and three relevant tags for the following note content:\n\n{content}"}
    ]
    response = call_llm_model(model, messages)
    
    # Parse the response
    try:
        title_line = response.split('\n')[0]
        tags_line = response.split('\n')[1]
        
        title = title_line.replace('Title:', '').strip()
        tags = [tag.strip() for tag in tags_line.replace('Tags:', '').split(',')]
        
        return {
            'title': title,
            'tags': tags[:3]  # Ensure we only get 3 tags
        }
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return {
            'title': 'Untitled Note',
            'tags': ['untagged']
        }

# A function to translate to target language
def translate_to_language(text, target_language):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that translates English to other languages."},
        {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
    ]
    translation = call_llm_model(model, messages)
    return translation

if __name__ == "__main__":
    # Test note generation
    sample_content = "Yesterday I learned about quantum computing and its potential impact on cryptography. The concept of qubits and superposition is fascinating. This could revolutionize how we think about data security."
    result = generate_note_metadata(sample_content)
    print("Generated Metadata:")
    print(f"Title: {result['title']}")
    print(f"Tags: {', '.join(result['tags'])}")