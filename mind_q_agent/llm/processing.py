import re
from typing import List, Tuple, Set

class ResponseProcessor:
    """
    Processes LLM responses to extract metadata like citations.
    """
    # Pattern to match [Source: filename] or (Source: filename)
    CITATION_PATTERN = r'[\[\(]Source:\s*(.*?)[\]\)]'

    def extract_citations(self, text: str) -> Tuple[str, List[str]]:
        """
        Extracts unique sources from the text.
        Returns:
            - The original text (or cleaned if we decide to remove inline tags later)
            - A list of unique source identifiers
        """
        matches = re.findall(self.CITATION_PATTERN, text, re.IGNORECASE)
        
        # Deduplicate and clean whitespace
        sources: Set[str] = set()
        for match in matches:
            # Handle comma-separated sources if any, e.g. [Source: doc1, doc2]
            parts = [s.strip() for s in match.split(',')]
            sources.update(parts)
            
        return text, list(sorted(sources))

response_processor = ResponseProcessor()
