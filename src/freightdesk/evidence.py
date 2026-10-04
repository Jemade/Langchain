import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from rank_bm25 import BM25Okapi


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class PolicySearch:
    def __init__(self, directory: Path):
        self.docs = [
            Document(page_content=p.read_text(), metadata={"source": p.name, "category": p.stem})
            for p in sorted(directory.glob("*.md"))
        ]
        self.index = BM25Okapi([tokens(d.page_content) for d in self.docs]) if self.docs else None
        self.chain = RunnableLambda(self.search)

    def search(self, request):
        if not self.index:
            return []
        scores = self.index.get_scores(tokens(request["category"] + " " + request["details"]))
        matches = [
            {
                "source": d.metadata["source"],
                "text": d.page_content,
                "score": round(float(scores[i]), 4),
            }
            for i, d in enumerate(self.docs)
            if d.metadata["category"] == request["category"]
        ]
        return sorted(matches, key=lambda d: d["score"], reverse=True)[:2]
