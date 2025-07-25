from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import markdown
import os
from dotenv import load_dotenv

# Load .env for API key
load_dotenv()

app = Flask(__name__)

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("name")
    college = request.form.get("college")
    degree = request.form.get("degree")
    domain = request.form.get("domain")
    year = request.form.get("year")
    specializations = request.form.get("specializations", "")

    if not all([name, college, degree, domain, year, specializations]):
        return jsonify({"success": False, "error": "Please fill all fields!"})

    prompt = f"""
You are an expert AI roadmap advisor.

Generate a detailed career roadmap for a student named {name}, who is currently in their {year} year of {degree} in the {domain} domain at {college}. Their interests include: {specializations}.

Give a year-by-year breakdown starting from their current academic year ({year}) up to graduation. For each year, mention:

- Skills to focus on
- Projects to build
- Internship or research guidance
- Tools/technologies to learn
- Certifications (if any)

Present the roadmap in clear Markdown format using headings and tables where needed. Make it beginner-friendly, inspiring, and visually readable.
"""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3-235b-a22b-07-25:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI roadmap advisor."},
                {"role": "user", "content": prompt}
            ]
        )
        roadmap_md = response.choices[0].message.content
        roadmap_html = markdown.markdown(roadmap_md, extensions=['tables', 'fenced_code'])

        # Add spacing between tables for better readability
        roadmap_html = roadmap_html.replace("</table>", "</table><br><br>")

        return jsonify({"success": True, "roadmap": roadmap_html})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True)
