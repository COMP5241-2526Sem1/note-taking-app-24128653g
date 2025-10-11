
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
token = os.environ.get('GITHUB_TOKEN')
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

if not token:
    print("Warning: GITHUB_TOKEN not set — LLM features will fail until configured")


# A function to call an LLM model and return the response
def call_llm_model(model, messages, temperature=1.0, top_p=1.0):
    if not token:
        raise RuntimeError('GITHUB_TOKEN is not configured; cannot call LLM')
    try:
        client = OpenAI(base_url=endpoint, api_key=token)
        response = client.chat.completions.create(
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            model=model,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f'LLM call failed: {e}') from e

# A function to generate note title and tags from content
def generate_note_metadata(content):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that analyzes text and generates appropriate titles and tags. Return your response in the format: 'Title: <title>\nTags: <tag1>, <tag2>, <tag3>'"},
        {"role": "user", "content": f"Generate a title and three relevant tags for the following note content:\n\n{content}"}
    ]
    try:
        response = call_llm_model(model, messages)
        title_line = response.split('\n')[0]
        tags_line = response.split('\n')[1]
        title = title_line.replace('Title:', '').strip()
        tags = [tag.strip() for tag in tags_line.replace('Tags:', '').split(',')]
        return {
            'title': title,
            'tags': tags[:3]
        }
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return {'title': 'Untitled Note', 'tags': ['untagged']}

# A function to translate to target language
def translate_to_language(text, target_language):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that translates English to other languages."},
        {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
    ]
    try:
        translation = call_llm_model(model, messages)
        return translation
    except Exception as e:
        print(f"LLM translation failed: {e}")
        return None

if __name__ == "__main__":
    # Test note generation
    sample_content = "Yesterday I learned about quantum computing and its potential impact on cryptography. The concept of qubits and superposition is fascinating. This could revolutionize how we think about data security."
    result = generate_note_metadata(sample_content)
    print("Generated Metadata:")
    print(f"Title: {result['title']}")
    print(f"Tags: {', '.join(result['tags'])}")