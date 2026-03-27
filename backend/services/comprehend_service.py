"""
Amazon Comprehend Service Wrapper.

Analyzes user feedback and reviews for sentiment and key phrases.
Uses rule-based analysis in mock mode.
"""


class ComprehendService:
    """Wrapper for Amazon Comprehend NLP operations."""

    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "love", "best", "clean", "fast", "efficient", "reliable", "helpful",
        "comfortable", "accessible", "convenient", "safe", "punctual",
    }
    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "worst", "dirty", "slow",
        "late", "delayed", "broken", "dangerous", "uncomfortable", "rude",
        "crowded", "expensive", "unreliable", "inaccessible", "confusing",
    }

    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def analyze_sentiment(self, text):
        """Analyze sentiment of text."""
        if self.use_mock:
            words = set(text.lower().split())
            pos = len(words & self.POSITIVE_WORDS)
            neg = len(words & self.NEGATIVE_WORDS)
            total = pos + neg
            if total == 0:
                sentiment = "NEUTRAL"
                scores = {"positive": 0.25, "negative": 0.25, "neutral": 0.45, "mixed": 0.05}
            elif pos > neg:
                sentiment = "POSITIVE"
                scores = {"positive": 0.8, "negative": 0.05, "neutral": 0.1, "mixed": 0.05}
            elif neg > pos:
                sentiment = "NEGATIVE"
                scores = {"positive": 0.05, "negative": 0.8, "neutral": 0.1, "mixed": 0.05}
            else:
                sentiment = "MIXED"
                scores = {"positive": 0.35, "negative": 0.35, "neutral": 0.1, "mixed": 0.2}
            return {
                "text": text,
                "sentiment": sentiment,
                "scores": scores,
                "mode": "mock",
            }
        return None

    def detect_key_phrases(self, text):
        """Extract key phrases from text."""
        if self.use_mock:
            words = text.split()
            phrases = []
            # Simple mock: extract 2-3 word phrases
            for i in range(0, len(words) - 1, 2):
                phrase = " ".join(words[i:i + 2])
                phrases.append({
                    "text": phrase,
                    "score": 0.85,
                })
            return {
                "text": text,
                "key_phrases": phrases[:5],
                "mode": "mock",
            }
        return None

    def detect_language(self, text):
        """Detect the language of text."""
        if self.use_mock:
            return {
                "text": text[:50],
                "language": "en",
                "score": 0.99,
                "mode": "mock",
            }
        return None

    def batch_analyze_sentiment(self, texts):
        """Analyze sentiment for multiple texts."""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results

    def health_check(self):
        return {
            "service": "Amazon Comprehend",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "capabilities": ["sentiment", "key_phrases", "language_detection"],
        }
