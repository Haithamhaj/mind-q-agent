import logging
import re
from typing import Dict, List, Set, Any

import spacy
from dateutil.parser import parse as parse_date

logger = logging.getLogger(__name__)

class EntityExtractor:
    """
    Extracts structured entities and concepts from text using spaCy and Regex.
    
    Capabilities:
    - Named Entities (Person, Org, GPE) via spaCy.
    - Dates via Regex + dateutil parsing.
    - Emails via Regex.
    - General Concepts (deduplicated noun phrases).
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the extractor with a specific spaCy model.
        
        Args:
            model_name: spaCy model to load (default: en_core_web_sm)
        """
        try:
            logger.info(f"Loading spaCy model: {model_name}...")
            if not spacy.util.is_package(model_name):
                logger.warning(f"Model {model_name} not found. Downloading...")
                spacy.cli.download(model_name)
                
            self.nlp = spacy.load(model_name)
            logger.info("spaCy model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise RuntimeError(f"EntityExtractor init failed: {e}") from e

    def extract_all(self, text: str) -> Dict[str, List[Any]]:
        """
        Extract all supported entity types from text.
        
        Args:
            text: Input text content
            
        Returns:
            Dictionary with keys: entities, dates, emails, concepts
        """
        if not text or not text.strip():
            return {
                "entities": [],
                "dates": [],
                "emails": [],
                "concepts": []
            }

        doc = self.nlp(text)
        
        return {
            "entities": self._extract_named_entities(doc),
            "dates": self._extract_dates(text),
            "emails": self._extract_emails(text),
            "concepts": self._extract_concepts(doc)
        }

    def _extract_named_entities(self, doc) -> List[Dict[str, str]]:
        """Extract PERSON, ORG, GPE entities."""
        entities = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                clean_text = ent.text.strip()
                if len(clean_text) >= 3:
                    entities.append({
                        "text": clean_text,
                        "label": ent.label_
                    })
        return entities

    def _extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract and normalize dates using regex and dateutil."""
        # Simple regex for common date formats (YYYY-MM-DD, DD Month YYYY)
        # This is a basic pass, could be expanded.
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b', # 2023-01-01
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', # 1 Jan 2023
        ]
        
        found_dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                try:
                    dt = parse_date(date_str)
                    found_dates.append({
                        "original": date_str,
                        "iso": dt.strftime("%Y-%m-%d")
                    })
                except Exception:
                    continue # Skip invalid dates
                    
        return found_dates

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))

    def _extract_concepts(self, doc) -> List[str]:
        """
        Extract general concepts (Noun Chunks).
        Filters out stop words and short tokens.
        """
        concepts = set()
        for chunk in doc.noun_chunks:
            # Filter logic:
            # 1. Root must be a noun
            # 2. Not purely stop words
            # 3. Length > 2 characters
            clean_text = chunk.text.strip().lower()
            if len(clean_text) > 2 and not chunk.root.is_stop:
                concepts.add(clean_text)
        
        return list(concepts)
