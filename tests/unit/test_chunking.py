"""Tests unitaires -- module chunking. Absent du projet original."""
import pytest
from src.rag.ingestion.chunking import chunk_pages, _detect_section


class TestChunkPages:
    def _make_pages(self, text: str, source: str = "test.pdf") -> list[dict]:
        return [{"text": text, "page": 1, "source": source}]

    def test_retourne_des_chunks(self):
        pages = self._make_pages("A" * 1000)
        chunks = chunk_pages(pages)
        assert len(chunks) > 0

    def test_chunk_non_vide(self):
        pages = self._make_pages("Hello World " * 50)
        chunks = chunk_pages(pages)
        for c in chunks:
            assert len(c.text.strip()) >= 30

    def test_metadonnees_presentes(self):
        pages = self._make_pages("Content " * 100, source="test.pdf")
        chunks = chunk_pages(pages)
        for c in chunks:
            assert c.source == "test.pdf"
            assert c.page == 1
            assert isinstance(c.chunk_index, int)
            assert isinstance(c.id, str) and len(c.id) == 36

    def test_detection_bp_code(self):
        pages = self._make_pages(
            "SUS02-BP01 Scale workload infrastructure dynamically. "
            "Use elasticity of the cloud to scale your infrastructure. " * 20
        )
        chunks = chunk_pages(pages)
        bp_chunks = [c for c in chunks if c.bp_code is not None]
        assert len(bp_chunks) > 0
        assert any(c.bp_code == "SUS02-BP01" for c in bp_chunks)

    def test_page_vide_ignoree(self):
        pages = [{"text": "   \n  ", "page": 1, "source": "test.pdf"}]
        chunks = chunk_pages(pages)
        assert len(chunks) == 0


class TestDetectSection:
    def test_detecte_bp_code(self):
        text = "SUS04-BP03 Use policies to manage the lifecycle..."
        assert "SUS04-BP03" in _detect_section(text)

    def test_texte_vide(self):
        assert _detect_section("   ") == "Document"
