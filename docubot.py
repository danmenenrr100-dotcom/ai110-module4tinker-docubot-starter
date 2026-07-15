"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index
- Retrieving relevant snippets
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini
"""

import os
import glob
import re


class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()

        # Build retrieval index
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")

        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()

                filename = os.path.basename(path)
                docs.append((filename, text))

        return docs

    # -----------------------------------------------------------
    # Index Construction
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example:
        {
            "token": ["AUTH.md"],
            "database": ["SETUP.md"]
        }
        """
        index = {}

        for filename, text in documents:
            words = re.findall(r"\b\w+\b", text.lower())
            unique_words = set(words)

            for word in unique_words:
                if word not in index:
                    index[word] = []

                index[word].append(filename)

        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a simple relevance score for how well the text matches the query.

        Higher score means the snippet is more relevant.
        """
        stop_words = {
            "the", "is", "a", "an", "to", "of", "in", "on", "for", "and",
            "how", "do", "i", "where", "which", "what", "does", "all", "with"
        }

        query_words = re.findall(r"\b\w+\b", query.lower())
        query_words = [word for word in query_words if word not in stop_words]

        text_words = re.findall(r"\b\w+\b", text.lower())

        score = 0

        for word in query_words:
            score += text_words.count(word)

        # Small bonus if the exact query appears in the snippet
        if query.lower() in text.lower():
            score += 3

        return score

    def retrieve(self, query, top_k=3):
        """
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        stop_words = {
            "the", "is", "a", "an", "to", "of", "in", "on", "for", "and",
            "how", "do", "i", "where", "which", "what", "does", "all", "with"
        }

        query_words = re.findall(r"\b\w+\b", query.lower())
        query_words = [word for word in query_words if word not in stop_words]

        if not query_words:
            return []

        # Use the inverted index to find candidate documents
        candidate_filenames = set()

        for word in query_words:
            if word in self.index:
                candidate_filenames.update(self.index[word])

        if not candidate_filenames:
            return []

        results = []

        for filename, text in self.documents:
            if filename not in candidate_filenames:
                continue

            # Split the document into non-empty lines
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            # Create small overlapping snippets of 3 lines each.
            # This keeps headings/endpoints connected to their descriptions.
            for i in range(len(lines)):
                snippet = "\n".join(lines[i:i + 3])
                score = self.score_document(query, snippet)

                if score > 0:
                    results.append((filename, snippet, score))

        # Sort from strongest match to weakest match
        results.sort(key=lambda item: item[2], reverse=True)

        if not results:
            return []

        # Keep only results reasonably close to the best match.
        # This removes weak snippets that share only one vague word.
        best_score = results[0][2]
        filtered_results = []

        for filename, snippet, score in results:
            if score >= best_score * 0.5:
                filtered_results.append((filename, snippet, score))

        return [
            (filename, snippet)
            for filename, snippet, score in filtered_results[:top_k]
        ]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []

        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        RAG mode.
        Uses retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used for naive generation mode.
        """
        return "\n\n".join(text for _, text in self.documents)