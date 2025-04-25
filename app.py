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
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
        .container { max-width: 700px; margin: 60px auto; background: #ffffff; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); }
        h2 { text-align: center; margin-bottom: 30px; color: #333; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type=text] {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border-radius: 10px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }
        button {
            padding: 12px 20px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .check-btn {
            background-color: #007BFF;
            color: white;
        }
        .check-btn:hover {
            background-color: #0056b3;
        }
        .copy-btn {
            background-color: #28a745;
            color: white;
            margin-top: 10px;
        }
        .copy-btn:hover {
            background-color: #1e7e34;
        }
        .paste-btn {
            background-color: #ffc107;
            color: black;
        }
        .paste-btn:hover {
            background-color: #e0a800;
        }
        .result {
            margin-top: 20px;
        }
        .final-url {
            background: #eef;
            padding: 12px;
            border-radius: 8px;
            word-break: break-all;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔗 URL Redirection Checker</h2>
        <form method="POST">
            <div class="input-group">
                <input type="text" id="url-input" name="url" placeholder="Paste URL here" required>
                <button type="button" class="paste-btn" onclick="pasteFromClipboard()">📋 Paste</button>
            </div>
            <button type="submit" class="check-btn">Check Redirect</button>
        </form>

        {% if final_url %}
        <div class="result">
            <h4>Final Destination URL:</h4>
            <div class="final-url" id="final-url">{{ final_url }}</div>
            <button class="copy-btn" onclick="copyToClipboard()">📋 Copy Final URL</button>
        </div>
        {% endif %}
    </div>

    <script>
        function copyToClipboard() {
            const text = document.getElementById('final-url').innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('✅ Final URL copied to clipboard!');
            });
        }

        function pasteFromClipboard() {
            navigator.clipboard.readText().then(text => {
                document.getElementById('url-input').value = text;
            }).catch(err => {
                alert('❌ Failed to read clipboard content.');
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
