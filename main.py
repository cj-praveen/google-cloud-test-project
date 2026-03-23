from flask import Flask, render_template, request, jsonify
import requests, re, os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_website():
    try:
        data = request.get_json()
        user_input = data.get("prompt")

        if not user_input:
            return jsonify({"error": "Prompt is required"}), 400

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional web developer. "
                        "Generate a complete responsive HTML page with inline CSS and minimal JavaScript. "
                        "Return ONLY raw HTML code. No markdown. No explanation."
                    )
                },
                {
                    "role": "user",
                    "content": f"Create a website: {user_input}"
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({
                "error": "Groq API error",
                "details": response.text
            }), 500

        result = response.json()

        generated_code = result["choices"][0]["message"]["content"]

      
        generated_code = re.sub(r"```html|```", "", generated_code).strip()

        return jsonify({"code": generated_code})

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
