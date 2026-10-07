"""
Fanlar va mavzular daraxti (Topic Tree) moduli.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from config import DATA_DIR, SUBJECTS

TOPICS_FILE = DATA_DIR / "topics.json"

class TopicTree:
    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or TOPICS_FILE
        self.tree: Dict[str, List[str]] = self._load_topics()

    def _load_topics(self) -> Dict[str, List[str]]:
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {s: [] for s in SUBJECTS}

    def get_subjects(self) -> List[str]:
        return list(self.tree.keys())

    def get_topics(self, subject: str) -> List[str]:
        return self.tree.get(subject, [])

    def is_valid_topic(self, subject: str, topic: str) -> bool:
        return topic in self.tree.get(subject, [])

    def find_matching_topic(self, subject: str, query: str) -> Optional[str]:
        query_lower = query.lower()
        topics = self.get_topics(subject)
        for t in topics:
            if query_lower in t.lower() or t.lower() in query_lower:
                return t
        return None

topic_tree = TopicTree()
