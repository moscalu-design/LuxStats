from __future__ import annotations

import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def streamlit_server():
    streamlit_bin = shutil.which("streamlit")
    if streamlit_bin is None:
        pytest.skip("streamlit executable is not installed")
    port = _free_port()
    proc = subprocess.Popen(
        [
            streamlit_bin,
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(port),
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.time() + 25
        url = f"http://localhost:{port}"
        while time.time() < deadline:
            if proc.poll() is not None:
                output = proc.stdout.read() if proc.stdout else ""
                pytest.fail(f"Streamlit exited before serving the app:\n{output}")
            try:
                import urllib.request

                with urllib.request.urlopen(f"{url}/_stcore/health", timeout=1) as response:
                    if response.read().decode("utf-8") == "ok":
                        break
            except Exception:
                time.sleep(0.25)
        else:
            pytest.fail("Streamlit did not become healthy within 25 seconds")
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_home_search_and_commune_portal(streamlit_server: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 900})
        page.goto(streamlit_server, wait_until="networkidle")
        expect(page.get_by_text("Find official Luxembourg statistics in seconds")).to_be_visible(timeout=20000)
        search = page.get_by_placeholder("Search housing prices, salaries, population, inflation…")
        search.fill("Hesperange")
        search.press("Enter")
        expect(page.get_by_text("Hesperange commune profile")).to_be_visible()
        page.get_by_role("button", name="Open commune profile").click()
        expect(page.get_by_text("Choose a commune and explore local statistics in one place.")).to_be_visible(timeout=30000)
        expect(page.get_by_role("heading", name="Hesperange")).to_be_visible()
        browser.close()
