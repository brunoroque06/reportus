import subprocess
import time
import urllib.error
import urllib.request

import pytest
from playwright import sync_api

port = 8501
host = f"http://localhost:{port}"


@pytest.fixture(autouse=True, scope="module")
def start_app():
    with subprocess.Popen(
        [
            "streamlit",
            "run",
            "main.py",
            "--browser.serverPort",
            str(port),
            "--server.headless",
            "true",
        ]
    ) as app:
        while True:
            try:
                with urllib.request.urlopen(host) as r:
                    if r.code == 200:
                        break
            except urllib.error.URLError:
                pass
            time.sleep(1)
        yield
        app.terminate()


@pytest.mark.parametrize("url", ["DTVP-3", "DTVP-A", "MABC", "SPM"])
def test_pages(page: sync_api.Page, url: str):
    page.goto(f"{host}/{url}")
    page.wait_for_selector(".stApp", timeout=5000)
    page.wait_for_timeout(2000)  # what to wait for exactly?
    assert page.locator(".stException").count() == 0
