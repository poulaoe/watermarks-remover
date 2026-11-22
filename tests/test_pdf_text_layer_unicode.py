"""PDF logical text-layer Unicode inspection tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "service" / "scripts"))

import container_meta


class FakeProcess:
    def __init__(self, command, *, stdout, returncode=0, timeout=False):
        self.command = command
        self.stdout = stdout
        self.returncode = returncode
        self.timeout = timeout
        self.timed_out_once = False

    def communicate(self, input=None, timeout=None):
        self.stdout.write(self.output)
        if self.timeout and not self.timed_out_once:
            self.timed_out_once = True
            raise subprocess.TimeoutExpired(self.command, timeout)
        return None, None

    def kill(self):
        self.returncode = -9

    output = b""


def fake_popen(monkeypatch, output=b"", returncode=0, timeout=False):
    def factory(command, **kwargs):
        process = FakeProcess(command, stdout=kwargs["stdout"], returncode=returncode, timeout=timeout)
        process.output = output
        return process

    monkeypatch.setattr(container_meta.subprocess, "Popen", factory)


def test_pdf_text_layer_detects_zero_width_space(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda name: "/usr/bin/pdftotext")
    fake_popen(monkeypatch, b"visible\u200bhidden".decode("unicode_escape").encode("utf-8"))

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\\n")

    assert report["available"] is True
    assert report["suspicious_total"] == 1
    assert any(hit["codepoint"] == "U+200B" for hit in report["hits"])
    assert report["truncated"] is False


def test_pdf_text_layer_is_inconclusive_when_poppler_missing(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda _name: None)

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\\n")

    assert report["available"] is False
    assert "not scanned" in report["error"]


def test_pdf_text_layer_is_inconclusive_when_extraction_fails(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda name: "/usr/bin/pdftotext")
    fake_popen(monkeypatch, returncode=1)

    report = container_meta._inspect_pdf_text_layer(b"not a PDF")

    assert report["available"] is False
    assert "status 1" in report["error"]


def test_pdf_text_layer_timeout_is_inconclusive(monkeypatch):
    monkeypatch.setattr(container_meta, "which", lambda name: "/usr/bin/pdftotext")
    fake_popen(monkeypatch, timeout=True)

    report = container_meta._inspect_pdf_text_layer(b"%PDF-1.7\\n")

    assert report["available"] is False
    assert "timed out" in report["error"]
