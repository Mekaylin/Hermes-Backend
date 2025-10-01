"""Simple script to validate OPENAI_API_KEY and model access with a tiny dry-run.

Usage:
    python backend/scripts/check_openai.py

It returns 0 on success and prints model info or error message on failure.
"""
import os
import sys

try:
    import openai
except Exception as e:
    print('openai package not installed:', e)
    sys.exit(2)


def main():
    key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4')
    if not key:
        print('OPENAI_API_KEY not set in environment')
        sys.exit(1)

    openai.api_key = key
    try:
        # Simple list models call or a small completions call depending on installed SDK
        if hasattr(openai, 'Model'):
            # Newer SDK surfaces
            models = openai.Model.list()
            names = [m.id for m in models.data]
            print('Available models (sample):', names[:10])
            if model not in names:
                print(f"Configured model '{model}' not found in model list")
                sys.exit(3)
        else:
            # Older SDK fallback: attempt a tiny chat completion
            res = openai.ChatCompletion.create(model=model, messages=[{'role':'user','content':'say hi'}], max_tokens=1)
            print('Model call succeeded (demo)')
    except Exception as e:
        print('OpenAI test call failed:', e)
        sys.exit(4)

    print('OpenAI configuration looks good for model:', model)


if __name__ == '__main__':
    main()
