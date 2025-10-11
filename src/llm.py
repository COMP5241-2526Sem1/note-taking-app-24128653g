import os
from dotenv import load_dotenv
try:
    from openai import OpenAI
except Exception:
    # If the modern OpenAI client isn't available, we'll fallback at call time to the classic openai package
    OpenAI = None

# Load environment variables
load_dotenv()  # Loads environment variables from .env
token = os.environ.get('GITHUB_TOKEN')
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

if not token:
    # Don't raise at import time; instead functions will raise a clear error if token missing.
    # But log to help diagnostics.
    print("Warning: GITHUB_TOKEN not set — LLM features will fail until configured")

# A function to call an LLM model and return the response 
def call_llm_model(model, messages, temperature=1.0, top_p=1.0):    
    if not token:
        raise RuntimeError('GITHUB_TOKEN is not configured; cannot call LLM')

    # Try the modern OpenAI client first (if available)
    if OpenAI is not None:
        try:
            client = OpenAI(base_url=endpoint, api_key=token)
            response = client.chat.completions.create(
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                model=model,
            )
            # Compatible with the modern client response shape
            try:
                return response.choices[0].message.content
            except Exception:
                # Try dict-style access as fallback
                return response['choices'][0]['message']['content']
        except Exception as primary_exc:
            primary_error = primary_exc
    else:
        primary_error = None

    # Fallback: try the classic openai package API
    try:
        import openai as openai_mod
        # configure key/base
        openai_mod.api_key = token
        # If endpoint is a custom base, configure it; classic client may use api_base
        try:
            openai_mod.api_base = endpoint
        except Exception:
            pass

        resp = openai_mod.ChatCompletion.create(model=model, messages=messages, temperature=temperature, top_p=top_p)
        # Try attribute access then mapping access
        try:
            return resp.choices[0].message.content
        except Exception:
            try:
                return resp['choices'][0]['message']['content']
            except Exception:
                raise RuntimeError(f'Fallback openai returned unexpected response: {resp}')
    except Exception as fallback_exc:
        # Combine errors for diagnostics
        raise RuntimeError(f'LLM call failed; primary error: {primary_error}; fallback error: {fallback_exc}') from fallback_exc

# A function to generate note title and tags from content
def generate_note_metadata(content):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that analyzes text and generates appropriate titles and tags. Return your response in the format: 'Title: <title>\nTags: <tag1>, <tag2>, <tag3>'"},
        {"role": "user", "content": f"Generate a title and three relevant tags for the following note content:\n\n{content}"}
    ]
    # Try remote LLM first
    try:
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

    except Exception as e:
        print(f"LLM generation failed: {e}")

    # Fallback: simple heuristic-based generation so the endpoint remains usable
    # Title: first non-empty sentence or first 6 words
    try:
        first_sentence = content.split('.')
        if first_sentence:
            title_candidate = first_sentence[0].strip()
        else:
            title_candidate = ''
        if not title_candidate:
            title_candidate = ' '.join(content.strip().split()[:6])
        title_candidate = title_candidate[:120]  # cap length

        # Tags: take the top 3 words excluding stopwords
        stopwords = set(['the', 'and', 'a', 'an', 'of', 'to', 'in', 'for', 'on', 'with', 'is', 'was', 'it'])
        words = [w.strip('.,!?').lower() for w in content.split() if w.strip('.,!?')]
        freq = {}
        for w in words:
            if w in stopwords or len(w) < 3:
                continue
            freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        tags = [w for w,c in sorted_words[:3]]
        if not tags:
            tags = ['untagged']

        return {
            'title': title_candidate or 'Untitled Note',
            'tags': tags
        }
    except Exception as e:
        print(f"Fallback generation failed: {e}")
        return {'title': 'Untitled Note', 'tags': ['untagged']}

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