import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, Response, stream_with_context
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from bson import ObjectId
import markdown
import json
import feedparser
import requests
import re

from parser.file_reader import read_file
from parser.simplifier import simplify_text, simplify_text_stream

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

mongo_uri = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI")
if not mongo_uri:
    raise RuntimeError("No MongoDB URI found. Set MONGO_URI or MONGODB_URI in .env")

if "?" in mongo_uri:
    head, tail = mongo_uri.split("?", 1)
    if head.endswith("/"):
        head = head + "legalclause"
    elif "/" not in head.split("://", 1)[1]:
        head = head + "/legalclause"
    mongo_uri = head + "?" + tail
else:
    after_scheme = mongo_uri.split("://", 1)[1]
    if "/" not in after_scheme:
        if mongo_uri.endswith("/"):
            mongo_uri = mongo_uri + "legalclause"
        else:
            mongo_uri = mongo_uri + "/legalclause"

app.config["MONGO_URI"] = mongo_uri

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

class User(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.email = doc.get("email")

@login_manager.user_loader
def load_user(user_id):
    try:
        doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(doc) if doc else None
    except Exception:
        return None

WHITELIST = {"login", "register", "static", "favicon"}

@app.before_request
def require_login_for_all():
    endpoint = (request.endpoint or "").split(".")[-1]
    if endpoint in WHITELIST or (request.endpoint or "").startswith("static"):
        return
    if current_user.is_authenticated:
        return
    return redirect(url_for("login", next=request.path))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Please provide email and password", "warning")
            return redirect(url_for("register"))
        if mongo.db.users.find_one({"email": email}):
            flash("Email already registered", "danger")
            return redirect(url_for("register"))
        hashpw = bcrypt.generate_password_hash(password).decode()
        mongo.db.users.insert_one({"email": email, "password": hashpw})
        flash("Registered! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user_doc = mongo.db.users.find_one({"email": email})
        if user_doc and bcrypt.check_password_hash(user_doc["password"], password):
            user_obj = User(user_doc)
            login_user(user_obj)
            flash("Logged in successfully.", "success")
            next_page = request.form.get("next") or request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("home"))
        flash("Invalid email or password", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        text_input = request.form.get('text', '')
        text = ""
        
        if file:
            try:
                text = read_file(file)
            except ValueError as e:
                return f"<h3>{str(e)}</h3>"
        elif text_input:
            text = text_input
        else:
            return "<h3>No file or text provided</h3>"
        
        return render_template('result.html', original_text=text)
        
    return render_template('upload.html')

@app.route('/stream_analysis', methods=['POST'])
@login_required
def stream_analysis():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return Response("No text provided", status=400)

    def generate():
        for chunk in simplify_text_stream(text):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='text/plain')

from parser.chat_engine import chat_with_gemini_stream

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat_api', methods=['POST'])
@login_required
def chat_api():
    try:
        data = request.get_json()
        message = data.get('message')
        history = data.get('history', [])
        
        if not message:
            return Response("No message provided", status=400)

        def generate():
            try:
                for chunk in chat_with_gemini_stream(message, history):
                    yield chunk
            except Exception as e:
                print(f"Error in chat stream: {e}")
                yield f"Error: {str(e)}"

        return Response(stream_with_context(generate()), mimetype='text/plain')
    except Exception as e:
        print(f"Error in chat_api: {e}")
        return Response(str(e), status=500)

@app.route('/news')
@login_required
def news():
    return render_template('news.html')




@app.route('/api/news')
@login_required
def get_news():
    category = request.args.get('category', 'national')
    rss_urls = {
        'national': 'https://www.thehindu.com/news/national/feeder/default.rss',
        'international': 'https://www.thehindu.com/news/international/feeder/default.rss',
        'business': 'https://www.thehindu.com/business/feeder/default.rss',
        'sport': 'https://www.thehindu.com/sport/feeder/default.rss',
        'entertainment': 'https://www.thehindu.com/entertainment/feeder/default.rss',
        'science': 'https://www.thehindu.com/sci-tech/science/feeder/default.rss'
    }

    
    url = rss_urls.get(category, rss_urls['national'])
    
    try:
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries:
            # Extract image if available
            image_url = None
            if 'media_content' in entry:
                image_url = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        image_url = link.get('href')
                        break
            
            # Fallback for image in description or summary
            if not image_url and 'summary' in entry:
                import re
                img_match = re.search(r'<img src="([^"]+)"', entry.summary)
                if img_match:
                    image_url = img_match.group(1)

            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'description': entry.summary if 'summary' in entry else '',
                'published': entry.published if 'published' in entry else '',
                'image': image_url
            })
        return json.dumps(news_items)
    except Exception as e:
        return json.dumps({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
