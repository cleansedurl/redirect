from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# ... rest of the code ...


import requests

def get_final_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Example usage
url_to_check = input("Enter a URL to check: ")
final_url = get_final_url(url_to_check)
print("Final URL:", final_url)

