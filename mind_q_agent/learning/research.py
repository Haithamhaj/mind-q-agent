import logging
import asyncio
from typing import List, Dict, Any
from mind_q_agent.learning.qa import QAService
from mind_q_agent.tools import YouTubeSearchTool, ArxivSearchTool

logger = logging.getLogger(__name__)

class ResearchAssistant:
    """
    Research Assistant Mode (Task 87).
    Perform deep dive analysis and generate reports.
    """
    def __init__(self):
        self.qa = QAService()
        self.youtube = YouTubeSearchTool()
        self.arxiv = ArxivSearchTool()

    async def generate_report(self, topic: str, depth: str = "brief") -> Dict[str, Any]:
        """
        Generate a comprehensive research report on a topic.
        depth: 'brief' or 'deep'
        """
        logger.info(f"Starting research on: {topic} ({depth})")
        
        # 1. Decompose topic into sub-questions (Mock Strategy)
        sub_questions = [
            f"What is {topic}?",
            f"Recent advances in {topic}",
            f"Key challenges in {topic}"
        ]
        
        if depth == "deep":
            sub_questions.extend([
                f"Future trends in {topic}",
                f"Tools and frameworks for {topic}"
            ])
            
        # 2. Key Insights Collection (Parallel)
        # In a real app, we'd fire off concurrent QA/Search tasks
        report_sections = []
        all_sources = []
        
        introduction = await self.qa.answer_question(f"Overview of {topic}")
        report_sections.append(f"# Research Report: {topic}\n\n## Executive Summary\n{introduction['answer']}\n")
        all_sources.extend(introduction.get('sources', []))

        # 3. Deep Dive Sections
        for q in sub_questions[1:]:
            # Use specific tools for different sections
            section_content = f"## {q}\n"
            
            # Fetch content
            try:
                # ArXiv for advances
                if "advances" in q:
                    papers = self.arxiv.search(topic, max_results=3)
                    section_content += "### Academic Research\n"
                    for p in papers:
                        section_content += f"- **{p['title']}**: {p['summary'][:200]}...\n"
                        all_sources.append({"type": "paper", "title": p['title'], "url": p['url']})

                # YouTube for challenges/tutorials
                elif "Tools" in q:
                    videos = self.youtube.search(topic + " tools", max_results=2)
                    section_content += "### Practical Guides\n"
                    for v in videos:
                        section_content += f"- **{v['title']}**: {v['url']}\n"
                        all_sources.append({"type": "video", "title": v['title'], "url": v['url']})
                else:
                    # General QA
                    ans = await self.qa.answer_question(q)
                    section_content += f"{ans['answer']}\n"
            
            except Exception as e:
                section_content += f"*(Could not fetch data for this section: {e})*\n"
            
            report_sections.append(section_content)

        # 4. Compilation
        final_report = "\n".join(report_sections)
        
        # Unique sources
        unique_sources = {s['url']: s for s in all_sources}.values()
        
        final_report += "\n## References\n"
        for s in unique_sources:
            final_report += f"- [{s.get('type', 'link').upper()}] {s.get('title')} - {s.get('url')}\n"

        return {
            "topic": topic,
            "report_markdown": final_report,
            "sources": list(unique_sources)
        }
