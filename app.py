from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Redirection Checker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        input[type=text] { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 10px; }
        button { padding: 10px 15px; font-size: 16px; background: #007BFF; color: white; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; }
        .final-url { background: #eef; padding: 10px; border-radius: 6px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h2>URL Redirection Checker</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Paste URL here" required>
            <button type="submit">Check Redirect</button>
        </form>

        {% if final_url %}
        <div class="result">
            <h4>Final Destination URL:</h4>
            <div class="final-url" id="final-url">{{ final_url }}</div>
            <button onclick="copyToClipboard()">Copy</button>
        </div>
        {% endif %}
    </div>

    <script>
        function copyToClipboard() {
            const text = document.getElementById('final-url').innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('Final URL copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    final_url = None
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            final_url = response.url
        except requests.exceptions.RequestException as e:
            final_url = f"Error: {e}"
    return render_template_string(HTML_TEMPLATE, final_url=final_url)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
