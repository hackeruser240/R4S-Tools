from flask import Flask,request, render_template, send_file

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
from functions_folder.internal_link_optimizer import extract_internal_links, suggest_internal_links
from functions_folder.intent_classifier import classify_intents, summarize_intents
from collections import Counter

from functions_folder.trend_visualizer import create_sample_data, plot_trends


from functions_folder.ranking_forecast_model import (
    load_sample_data,
    ranking_forecast_model,
    visualize_forecast_results,
    generate_forecast_summary
)

from functions_folder.keyword_monitor import perform_google_search, find_keyword_rank, create_timestamped_folder, save_json
import os
from dotenv import load_dotenv; load_dotenv()
import logging
import pandas as pd
from logging.handlers import RotatingFileHandler



def mainroot_logger(script_name):
    log_dir = os.path.join(os.path.dirname(__file__), "functions_folder", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"LOGS-{script_name}.txt")
    logger = logging.getLogger("app.py")
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File Handler with rotation
        file_handler = RotatingFileHandler(log_path, maxBytes=500_000, backupCount=3, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # Formatter
        datefmt='%d-%b-%Y %I:%M %p'
        formatter = logging.Formatter(
            f"%(asctime)s [%(levelname)s] (%(module)s).py : %(message)s",
            datefmt=datefmt
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


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
    text = ""
    schema_type = "Article"

    if request.method == "POST":
        text = request.form.get("text", "")
        schema_type = request.form.get("schema_type", "Article")
        schema = generate_schema_ld(text, schema_type)

    return render_template("schema_generator.html", schema=schema, text=text, schema_type=schema_type)



@app.route("/content_gap_finder", methods=["GET", "POST"])
def content_gap_finder():
    results = []
    your_content = ""
    competitor_raw = ""

    if request.method == "POST":
        your_content = request.form.get("your_content", "").strip()
        competitor_raw = request.form.get("competitor_content", "").strip()
        competitor_texts = [line.strip() for line in competitor_raw.split("\n") if line.strip()]

        print("Your content:", your_content)
        print("Competitor lines:", competitor_texts)

        try:
            results = find_content_gaps(your_content, competitor_texts, top_n=10)
            print("RESULTS:", results)
        except Exception as e:
            print("Error in content gap finder:", e)
            results = []
    print("Sending to template:", results)
    return render_template("content_gap_finder.html",
                           results=results,
                           your_content=your_content,
                           competitor_raw=competitor_raw)

@app.route("/headline_optimizer", methods=["GET", "POST"])
def headline_optimizer():
    result = None
    headline=""
    if request.method == "POST":
        headline = request.form["headline"]
        result = score_headline(headline)
    return render_template("headline_optimizer.html", result=result, headline=headline)


@app.route("/brief_generator", methods=["GET", "POST"])
def brief_generator():
    result = None
    if request.method == "POST":
        seed_text = request.form["seed_text"]
        faq_count = int(request.form.get("faq_count", 5))
        result = generate_brief(seed_text, faq_count)
    return render_template("brief_generator.html", result=result)


@app.route("/internal_link_optimizer", methods=["GET", "POST"])
def internal_link_optimizer():
    suggestions = []
    url_input = ""
    max_links_input = "8"

    if request.method == "POST":
        url_input = request.form.get("url", "").strip()
        max_links_input = request.form.get("max_links", "10").strip()

        try:
            max_links = int(max_links_input)
        except ValueError:
            max_links = 10  # fallback if input is invalid

        if url_input:
            print(f"🔍 Crawling homepage: {url_input}")
            slugs, error = extract_internal_links(url_input, max_links=max_links)
            if not error and slugs:
                suggestions = suggest_internal_links(slugs, url_input, top_n=3)

    return render_template(
        "internal_link_optimizer.html",
        suggestions=suggestions,
        url_input=url_input,
        max_links_input=max_links_input
    )

#============================================================
#MODULE 3
#============================================================

@app.route('/intent_classifier', methods=['GET', 'POST'])
def intent_classifier():
    result = {}
    intent_counts = {}
    text_list=[]
    if request.method == 'POST':
        user_input = request.form['keywords']
        text_list = [line.strip() for line in user_input.split('\n') if line.strip()]
        result = classify_intents(text_list)
        intent_counts = Counter(result.values())
    return render_template('intent_classifier.html', result=result, intent_counts=intent_counts, content=text_list)

@app.route('/trend_visualizer', methods=['GET', 'POST'])
def trend_visualizer():
    chart_path = "static/trend_chart.html"
    if os.path.exists(chart_path):
        os.remove(chart_path)

    error_msg = ""
    raw_input = ""

    if request.method == 'POST':
        os.makedirs("static", exist_ok=True)  # Ensure static folder exists

        if 'sample' in request.form:
            df = create_sample_data()
            html_chart = plot_trends(df)
            with open(chart_path, "w", encoding="utf-8") as f:
                f.write(html_chart)
            raw_input = "Loaded sample data."

        elif 'csvfile' in request.files:
            file = request.files['csvfile']
            raw_input = file.filename
            try:
                df = pd.read_csv(file)
                html_chart = plot_trends(df)
                with open(chart_path, "w", encoding="utf-8") as f:
                    f.write(html_chart)
            except Exception as e:
                error_msg = f"Error processing CSV: {str(e)}"

    chart_exists = os.path.exists(chart_path)
    return render_template('trend_visualizer.html',
                           chart_exists=chart_exists,
                           chart_path=chart_path,
                           error_msg=error_msg,
                           raw_input=raw_input)


@app.route("/ranking_forecast", methods=["GET", "POST"])
def ranking_forecast():
    forecast_output = None
    chart_html = None
    summary_text = None
    keyword = ""
    forecast_horizon = 30
    show_form = False

    # If user clicked "Use Sample Data" (GET request)
    if request.method == "GET" and request.args.get("load_sample") == "true":
        show_form = True

    # If user submitted the form (POST request)
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        try:
            forecast_horizon = int(request.form.get("forecast_horizon", 30))
        except ValueError:
            forecast_horizon = 30

        if keyword:
            sample_data = load_sample_data(keyword=keyword)
            forecast_output = ranking_forecast_model(sample_data, forecast_horizon)
            chart_html = visualize_forecast_results(forecast_output)
            summary_text = generate_forecast_summary(forecast_output)
            show_form = True  # Show form again after processing

    return render_template("ranking_forecast.html",
                           keyword=keyword,
                           forecast_horizon=forecast_horizon,
                           forecast_output=forecast_output,
                           chart_html=chart_html,
                           summary_text=summary_text,
                           show_form=show_form)


@app.route("/keyword_monitor", methods=["GET", "POST"])
def keyword_monitor():
    logger = mainroot_logger("app.py")
    result = None
    keywords = ""
    tokenize = True

    if request.method == "POST":
        keywords = request.form.get("keywords", "")
        tokenize = bool(request.form.get("tokenize"))
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        api_key = os.getenv("GOOGLE_API_KEY", "your_api_key_here")
        cx_id = os.getenv("GOOGLE_CX_ID", "your_cx_id_here")
        folder = create_timestamped_folder()

        result = []
        for keyword in keyword_list:
            search_data = perform_google_search(keyword, api_key, cx_id, logger=logger)
            logger.info("Running from app.py")
            rank, matched_result = find_keyword_rank(keyword, search_data, logger=logger,use_tokenization=tokenize)

            summary = {
                "keyword": keyword,
                "rank": rank if rank else "Not found",
                "matched_result": matched_result if matched_result else {},
                "folder": folder
            }

            safe_name = keyword.replace(" ", "_").lower()
            save_json(search_data, folder, f"{safe_name}_full_data.json")
            save_json(summary, folder, f"{safe_name}_result.json")
            result.append(summary)

    return render_template("keyword_monitor.html", result=result, keywords=keywords, tokenize=tokenize)



application = app
if __name__=="__main__":
    app.run(debug=True)