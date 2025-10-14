import subprocess
import os
import uuid
import glob
import shutil
import webbrowser
from urllib.parse import urlparse
import sys
import pprint

def normalize_url(input_url):
    """Ensure the input is a valid, fully qualified URL."""
    input_url = input_url.strip()
    parsed = urlparse(input_url)

    # If it's a full URL with scheme and netloc, use it as-is
    if parsed.scheme and parsed.netloc:
        return input_url.rstrip("/")

    # If it's a bare domain, wrap it in https://
    domain = input_url.replace("/", "")
    return f"https://{domain}"

def run_lighthouse_audit(target_url):
    final_url = normalize_url(target_url)
    print(f"Running Lighthouse audit on: {final_url}")

    report_id = str(uuid.uuid4())
    output_dir = os.path.abspath(f"static/reports/{report_id}")
    os.makedirs(output_dir, exist_ok=True)
    output_base = os.path.join(output_dir, "report")

    command = [
        r"C:\Users\HP\AppData\Roaming\npm\lighthouse.cmd",
        final_url,
        "--output=json",
        "--output=html",
        f"--output-path={output_base}",
        "--quiet",
        "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage",
        "--chrome-path=C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "--timeout=120000"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

        html_candidates = glob.glob(output_base + "*.report.html")
        json_candidates = glob.glob(output_base + "*.report.json")

        html_path = output_base + ".html"
        json_path = output_base + ".json"

        if html_candidates:
            shutil.move(html_candidates[0], html_path)
        if json_candidates:
            shutil.move(json_candidates[0], json_path)

        if not os.path.exists(html_path):
            return {"error": "Lighthouse did not generate an HTML report."}

        return {
            "html": html_path.replace("\\", "/"),
            "json": json_path.replace("\\", "/"),
            "report_id": report_id,
            #"warning": f"Lighthouse exited with code {result.returncode}" if result.returncode != 0 else None
        }

    except FileNotFoundError as e:
        return {"error": f"Executable not found: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python performance_audit.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    result = run_lighthouse_audit(target_url)

    print("\n📊 Audit Result:")
    pprint.pprint(result)

    if "html" in result:
        full_path = os.path.abspath(result["html"])
        print(f"{full_path}")
        webbrowser.open(f'file:///{full_path}')
    else:
        print("⚠️ No HTML report generated.")