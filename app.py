from flask import Flask, request, render_template_string
import requests
import os
import re
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

app = Flask(__name__)

TELEGRAM_API_ID = int(os.environ.get("TG_API_ID"))
TELEGRAM_API_HASH = os.environ.get("TG_API_HASH")
TELEGRAM_CHANNEL = os.environ.get("TG_CHANNEL")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>RoarDeals Redirect Cleaner</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(to right, #fdfbfb, #ebedee);
      margin: 0;
      padding: 1em;
      display: flex;
      justify-content: center;
    }
    .container {
      background: white;
      padding: 1.5em;
      border-radius: 16px;
      width: 100%;
      max-width: 500px;
      box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }
    h2 {
      margin-top: 0;
      font-size: 1.6em;
      color: #333;
      text-align: center;
    }
    input[type=text], textarea {
      width: 100%;
      padding: 0.8em;
      margin-top: 1em;
      font-size: 1em;
      border-radius: 8px;
      border: 1px solid #ccc;
      transition: border-color 0.3s;
    }
    input:focus, textarea:focus {
      border-color: #0077cc;
      outline: none;
    }
    .btn {
      padding: 0.7em 1em;
      font-size: 1em;
      border: none;
      border-radius: 8px;
      margin-top: 1em;
      cursor: pointer;
      transition: background 0.3s;
      width: 100%;
    }
    .btn-primary {
      background: #0077cc;
      color: white;
    }
    .btn-primary:hover {
      background: #005fa3;
    }
    .btn-secondary {
      background: #f0f0f0;
      color: #333;
    }
    .btn-secondary:hover {
      background: #e0e0e0;
    }
    #copyMessage {
      color: green;
      font-size: 0.9em;
      margin-top: 0.5em;
      text-align: center;
      height: 1em;
    }
    .button-group {
      display: flex;
      gap: 0.5em;
      flex-direction: column;
    }
    @media(min-width: 500px) {
      .button-group {
        flex-direction: row;
      }
      .btn {
        width: auto;
      }
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <h2>RoarDeals Redirect Cleaner 🦁</h2>
    <form method=\"POST\">
      <div class=\"button-group\">
        <button type=\"button\" class=\"btn btn-secondary\" onclick=\"pasteFromClipboard()\">📋 Paste</button>
        <button type=\"submit\" class=\"btn btn-primary\">🔍 Extract & Clean</button>
      </div>
      <textarea name=\"message\" id=\"urlInput\" rows=\"4\" placeholder=\"Paste full message here...\" required>{{ original_text | default('') }}</textarea>
    </form>
    <form method=\"GET\" action=\"/fetch_telegram\">
      <button type=\"submit\" class=\"btn btn-secondary\">📥 Fetch Amazon Deals from Telegram</button>
    </form>

    {% if cleaned_text %}
    <textarea id=\"result\" rows=\"8\" readonly>{{ cleaned_text }}</textarea>
    <button class=\"btn btn-primary\" onclick=\"copyToClipboard()\">✅ Copy Result</button>
    <button class=\"btn btn-primary\" onclick=\"shareOnWhatsApp()\">📤 Share on WhatsApp</button>
    <div id=\"copyMessage\"></div>
    {% endif %}

    {% if telegram_msgs %}
    <h3 style=\"margin-top:1.5em;\">📦 Latest Telegram Deals</h3>
    {% for msg in telegram_msgs %}
      <textarea rows=\"6\" readonly style=\"margin-bottom:1em;\">{{ msg }}</textarea>
      <button class=\"btn btn-primary\" onclick=\"shareOnWhatsAppText(`{{ msg | safe }}`)">📤 Share This</button>
    {% endfor %}
    {% endif %}

    <p style=\"margin-top:2em;text-align:center;font-size:0.95em;color:#555;\">🔥 Grab the best deals now! Don't miss out!<br>👉 Join our <strong>RoarDeals WhatsApp Channel</strong> for daily loot alerts! 🛍️📲</p>
  </div>

  <script>
    function pasteFromClipboard() {
      navigator.clipboard.readText().then(text => {
        document.getElementById('urlInput').value = text;
      }).catch(() => alert("Clipboard access denied."));
    }

    function copyToClipboard() {
      const resultText = document.getElementById("result").value;
      const messageBox = document.getElementById("copyMessage");
      if (!resultText || resultText === "Invalid URL!") {
        messageBox.innerText = "Nothing to copy!";
        return;
      }
      navigator.clipboard.writeText(resultText).then(() => {
        messageBox.innerText = "✅ Copied to clipboard!";
        setTimeout(() => { messageBox.innerText = ""; }, 2000);
      });
    }

    function shareOnWhatsApp() {
      const message = document.getElementById("result").value;
      if (!message) return alert("No message to share!");
      const url = "https://wa.me/?text=" + encodeURIComponent(message);
      window.open(url, "_blank");
    }

    function shareOnWhatsAppText(text) {
      const url = "https://wa.me/?text=" + encodeURIComponent(text);
      window.open(url, "_blank");
    }
  </script>
</body>
</html>
"""

def cleanse_and_tag(url_str):
    try:
        url = requests.head(url_str, allow_redirects=True, timeout=10).url
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        if "amazon." in parsed.netloc:
            query.pop("tag", None)
            query.pop("ascsubtag", None)
            query.pop("ref", None)
            query["tag"] = ["roardeals0c-21"]

        if "flipkart." in parsed.netloc:
            query.pop("affid", None)
            query.pop("affExtParam1", None)
            query.pop("affExtParam2", None)
            query.pop("affExtParam", None)

        cleaned_query = urlencode(query, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=cleaned_query))
        return cleaned_url

    except Exception as e:
        return url_str  # return original if fails

def extract_and_replace_urls(text):
    urls = re.findall(r'https?://\S+', text)
    for u in urls:
        cleaned = cleanse_and_tag(u)
        text = text.replace(u, cleaned)

    cta = (
        "\n\n🔥 *Grab it before it’s gone!* "
        "🛒 Follow RoarDeals for daily deals!\n"
        "👉 Join our WhatsApp Channel now:  https://whatsapp.com/channel/0029VbAKok6BVJl77xRLF90s"
    )

    return text.strip() + cta

def fetch_telegram_amazon_messages(limit=5):
    async def fetch():
        async with TelegramClient('roardeals_session', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            entity = await client.get_entity(TELEGRAM_CHANNEL)
            history = await client(GetHistoryRequest(
                peer=entity,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            return [
                msg.message for msg in history.messages
                if msg.message and re.search(r'https?://(?:amzn\.to|www\.amazon\.\S+)', msg.message)
            ]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(fetch())

@app.route('/', methods=['GET', 'POST'])
def home():
    cleaned_text = None
    original_text = ''
    if request.method == 'POST':
        original_text = request.form['message']
        cleaned_text = extract_and_replace_urls(original_text)
    return render_template_string(HTML_TEMPLATE, cleaned_text=cleaned_text, original_text=original_text)

@app.route('/fetch_telegram')
def fetch_telegram():
    try:
        messages = fetch_telegram_amazon_messages(limit=5)
        cleaned = [extract_and_replace_urls(m) for m in messages]
        return render_template_string(HTML_TEMPLATE, telegram_msgs=cleaned)
    except Exception as e:
        return f"Error fetching messages: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
