from flask import Flask,request, render_template, send_file
#from functions import *

from functions_folder.performance_audit import run_lighthouse_audit
from functions_folder.content_scorer import content_scorer
from functions_folder.seo_analyzer import seo_analyzer
from functions_folder.crawler import crawl_site
from functions_folder.broken_link_checker import broken_link_checker
from functions_folder.redirect_mapper import redirect_mapper
from functions_folder.image_optimizer import image_optimizer
from functions_folder.schema_generator import generate_schema_ld
from functions_folder.internal_link_optimizer import suggest_internal_links
from functions_folder.content_gap_finder import find_content_gaps
from functions_folder.headline_optimizer import score_headline
from functions_folder.brief_generator import generate_brief
from functions_folder.topic_modeler import lda_topic_modeling, bert_topic_modeling, visualize_topics








import os 

app=Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
REPORT_FOLDER = os.path.join(app.root_path, 'static', 'reports')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config['APPLICATION_ROOT'] = '/aio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER



@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route('/aio', methods=['GET', 'POST'])
def aio():
    return render_template('homepage.html')


@app.route("/<name>")
def user(name ):
    return f"Hello {name}"

@app.route('/website-crawler', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        url = request.form['url']
        max_pages = int(request.form.get('max_pages', 50))
        results = crawl_site(url, max_pages=max_pages)
    return render_template('crawler.html', results=results)

@app.route('/seo_analyzer', methods=['GET', 'POST'])
def seo_analyzer_route():
    results = None
    error = None
    if request.method == 'POST':
        url = request.form['url']
        results = seo_analyzer(url)
        if 'error' in results:
            error = results['error']
            results = None
    return render_template('seo_analyzer.html', results=results, error=error)

@app.route("/performance_audit", methods=["GET", "POST"])
def performance_audit():
    if request.method == "POST":
        target_url = request.form.get("url")
        result = run_lighthouse_audit(target_url)

        if "error" in result:
                return render_template("performance_audit.html", error=result["error"])
        elif "warning" in result:
            return render_template("performance_audit.html", report_url=result["html"], report_id=result["report_id"], warning=result["warning"])

        return render_template(
            "performance_audit.html",
            report_url=result["html"],
            report_id=result["report_id"]
        )

    return render_template("performance_audit.html")

@app.route("/download_report/<report_id>")
def download_report(report_id):
    report_path = f"static/reports/{report_id}/report.html"
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Report not found", 404


@app.route("/content_scorer", methods=["GET", "POST"])
def content_scorer_route():
    result = None
    if request.method == "POST":
        content = request.form.get("content", "")
        reference = request.form.get("reference", "")
        if content and reference:
            result = content_scorer(content, reference)
    return render_template("content_scorer.html", result=result)

@app.route('/broken_link_checker', methods=['GET', 'POST'])
def broken_link_checker_route():
    results = None
    error = None
    if request.method == 'POST':
        url = request.form['url']
        results = broken_link_checker(url)
        if 'error' in results:
            error = results['error']
            results = None
    return render_template('broken_link_checker.html', results=results, error=error)

@app.route('/redirect_mapper', methods=['GET', 'POST'])
def redirect_mapper_route():
    results = None
    error = None
    if request.method == 'POST':
        url = request.form['url']
        results = redirect_mapper(url)
        if 'error' in results:
            error = results['error']
            results = None
    return render_template('redirect_mapper.html', results=results, error=error)

@app.route('/image_optimizer', methods=['GET', 'POST'])
def image_optimizer_route():
    results = None
    error = None

    if request.method == 'POST':
        file = request.files.get('image')
        width = request.form.get('width', type=int)
        height = request.form.get('height', type=int)
        output_format = request.form.get('format') or 'JPEG'
        quality = request.form.get('quality', type=int) or None

        if file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)

            resize_dims = (width, height) if width and height else None

            results = image_optimizer(
                image_path=image_path,
                resize_dims=resize_dims,
                output_format=output_format,
                quality=quality
            )

            if 'error' in results:
                error = results['error']
                results = None

    return render_template('image_optimizer.html', results=results, error=error)

#============================================================
#MODULE 2
#============================================================

@app.route("/topic_modeler", methods=["GET", "POST"])
def topic_modeler():
    topics = []
    raw_texts = ""
    method = "lda"
    num_topics = 3
    error = None
    show_viz = False

    if request.method == "POST":
        raw_texts = request.form["texts"]
        method = request.form["method"]
        num_topics = int(request.form.get("num_topics", 3))
        show_viz = request.form.get("show_viz") == "yes"

        texts = [line.strip() for line in raw_texts.strip().split("\n") if line.strip()]

        if method == "lda":
            topics, lda_model, corpus, dictionary = lda_topic_modeling(texts, num_topics=num_topics)
            if show_viz:
                visualize_topics("lda", lda_model=lda_model, corpus=corpus, dictionary=dictionary)

        elif method == "bert":
            if len(texts) < num_topics:
                error = f"You entered {len(texts)} text(s), but requested {num_topics} clusters. Please enter more texts or reduce the number of clusters."
            else:
                topics, embeddings, labels = bert_topic_modeling(texts, num_clusters=num_topics)
                if show_viz:
                    visualize_topics("bert", embeddings=embeddings, labels=labels)

    return render_template(
        "topic_modeler.html",
        topics=topics,
        raw_texts=raw_texts,
        method=method,
        num_topics=num_topics,
        error=error,
        show_viz=show_viz
    )



@app.route("/schema_generator", methods=["GET", "POST"])
def schema_generator():
    schema = None
    if request.method == "POST":
        text = request.form.get("text", "")
        schema_type = request.form.get("schema_type", "Article")
        schema = generate_schema_ld(text, schema_type)
    return render_template("schema_generator.html", schema=schema)


@app.route("/internal_link_optimizer", methods=["GET", "POST"])
def internal_link_optimizer():
    suggestions = None
    if request.method == "POST":
        pages = request.form["pages"].split(",")
        pages = [p.strip() for p in pages if p.strip()]
        
        raw_links = request.form["links"].split(",")
        links = []
        for link in raw_links:
            parts = link.strip().split("-")
            if len(parts) == 2:
                links.append((parts[0].strip(), parts[1].strip()))
        
        suggestions = suggest_internal_links(pages, links)

    return render_template("internal_link_optimizer.html", suggestions=suggestions)

@app.route("/content_gap_finder", methods=["GET", "POST"])
def content_gap_finder():
    results = None
    if request.method == "POST":
        your_content = request.form["your_content"]
        competitor_raw = request.form["competitor_content"]
        competitor_texts = [line.strip() for line in competitor_raw.strip().split("\n") if line.strip()]
        results = find_content_gaps(your_content, competitor_texts, top_n=10)
    return render_template("content_gap_finder.html", results=results)

@app.route("/headline_optimizer", methods=["GET", "POST"])
def headline_optimizer():
    result = None
    if request.method == "POST":
        headline = request.form["headline"]
        result = score_headline(headline)
    return render_template("headline_optimizer.html", result=result)


@app.route("/brief_generator", methods=["GET", "POST"])
def brief_generator():
    result = None
    if request.method == "POST":
        seed_text = request.form["seed_text"]
        faq_count = int(request.form.get("faq_count", 5))
        result = generate_brief(seed_text, faq_count)
    return render_template("brief_generator.html", result=result)


application = app
if __name__=="__main__":
    app.run(debug=True)