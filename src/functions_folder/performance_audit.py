# File: functions_folder/performance_audit.py

import subprocess
import os
import uuid

def run_lighthouse_audit(target_url):
    """Runs Lighthouse audit via subprocess and returns report paths."""
    report_id = str(uuid.uuid4())
    output_dir = f"static/reports/{report_id}"
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, "report.html")
    html_path = os.path.join(output_dir, "report.html").replace("\\", "/")

    json_path = os.path.join(output_dir, "report.json")

    command = [
        r"C:\Users\HP\AppData\Roaming\npm\lighthouse.cmd",
        target_url,
        "--output=json",
        "--output=html",
        f"--output-path={html_path}",
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
            # Still return the paths if files were generated
            if os.path.exists(html_path):
                return {
                    "html": html_path,
                    "json": json_path,
                    "report_id": report_id,
                    "warning": f"Lighthouse exited with code {result.returncode}. See logs for details."
                }
            return {"error": f"Lighthouse failed: {result.stderr}"}
        return {
            "html": html_path,
            "json": json_path,
            "report_id": report_id
        }
    except FileNotFoundError as e:
        return {"error": f"Executable not found: {e}"}
    

if __name__ == "__main__":
    import sys
    import pprint

    if len(sys.argv) != 2:
        print("Usage: python performance_audit.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    result = run_lighthouse_audit(target_url)

    print("\n📊 Audit Result:")
    pprint.pprint(result)