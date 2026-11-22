"""PDF logical text-layer Unicode inspection tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "service" / "scripts"))

import container_meta


def fake_run(monkeypatch, output=b"", returncode=0, timeout=False):
    def run(command, **kwargs):
        if timeout:
            raise subprocess.TimeoutExpired(command, kwargs.get("timeout"))
        kwargs["stdout"].write(output)
        return subprocess.CompletedProcess(command, returncode)

    monkeypatch.setattr(container_meta.subprocess, "run", run)


def test_pdf_text_layer_detects_zero_width_space(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda _name: "/usr/bin/pdftotext")
    fake_run(monkeypatch, "visible\u200bhidden".encode("utf-8"))

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\n")

    assert report["available"] is True
    assert report["suspicious_total"] == 1
    assert any(hit["codepoint"] == "U+200B" for hit in report["hits"])
    assert report["truncated"] is False


def test_pdf_text_layer_is_inconclusive_when_poppler_missing(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda _name: None)

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\n")

    assert report["available"] is False
    assert "not scanned" in report["error"]


def test_pdf_text_layer_is_inconclusive_when_extraction_fails(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda _name: "/usr/bin/pdftotext")
    fake_run(monkeypatch, returncode=1)

    report = container_meta._inspect_pdf_text_layer(b"not a PDF")

    assert report["available"] is False
    assert "status 1" in report["error"]


def test_pdf_text_layer_timeout_is_inconclusive(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda _name: "/usr/bin/pdftotext")
    fake_run(monkeypatch, timeout=True)

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\n")

    assert report["available"] is False
    assert "timed out" in report["error"]
