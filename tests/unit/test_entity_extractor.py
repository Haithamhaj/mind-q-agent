import pytest
import spacy
from unittest.mock import MagicMock, patch
from mind_q_agent.extraction.entity_extractor import EntityExtractor

class TestEntityExtractor:
    """Unit tests for EntityExtractor."""
    
    @pytest.fixture(scope="class")
    def extractor(self):
        """Initialize extractor once for all tests to save time loading model."""
        return EntityExtractor(model_name="en_core_web_sm")

    def test_init_success(self, extractor):
        """Test successful initialization."""
        assert extractor.nlp is not None
        assert "ner" in extractor.nlp.pipe_names

    def test_extract_all_empty(self, extractor):
        """Test handling empty input."""
        result = extractor.extract_all("")
        assert result["entities"] == []
        assert result["dates"] == []
        assert result["emails"] == []
        assert result["concepts"] == []

    def test_extract_named_entities(self, extractor):
        """Test Person, Org, GPE extraction."""
        text = "Elon Musk works at Tesla in Texas."
        result = extractor.extract_all(text)
        
        entities = result["entities"]
        texts = [e["text"] for e in entities]
        labels = {e["text"]: e["label"] for e in entities}
        
        assert "Elon Musk" in texts
        assert labels["Elon Musk"] == "PERSON"
        
        assert "Tesla" in texts
        assert labels["Tesla"] == "ORG"
        
        assert "Texas" in texts
        assert labels["Texas"] == "GPE"

    def test_extract_dates(self, extractor):
        """Test date extraction and normalization."""
        text = "Project started on 2023-01-01 and ends 5 May 2024."
        result = extractor.extract_all(text)
        
        dates = result["dates"]
        isos = [d["iso"] for d in dates]
        
        assert "2023-01-01" in isos
        assert "2024-05-05" in isos

    def test_extract_emails(self, extractor):
        """Test email extraction."""
        text = "Contact support@mindq.ai or admin@test.com for help."
        result = extractor.extract_all(text)
        
        emails = result["emails"]
        assert "support@mindq.ai" in emails
        assert "admin@test.com" in emails

    def test_extract_concepts(self, extractor):
        """Test noun phrase concept extraction."""
        text = "Artificial Intelligence is transforming the world."
        result = extractor.extract_all(text)
        
        concepts = result["concepts"]
        # "Artificial Intelligence" should be detected as a noun chunk
        assert "artificial intelligence" in concepts
        # "the world" is the full noun chunk
        assert "the world" in concepts

    def test_filter_short_entities(self, extractor):
        """Test that short entities (<3 chars) are ignored."""
        # 'Al' could be a person name but it's short (<3). 
        # Actually logic is >= 3. "Al" is length 2.
        text = "Al goes to NY." 
        # "NY" is GPE but length 2.
        result = extractor.extract_all(text)
        
        entities = [e["text"] for e in result["entities"]]
        assert "NY" not in entities
        assert "Al" not in entities
