import re
from typing import List

def extract_keywords(text: str, max_keywords: int = 25) -> List[str]:
    stopwords = {
        'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'on', 'for', 'with', 'as', 'was', 'at', 'by', 'an',
        'be', 'this', 'which', 'or', 'from', 'but', 'not', 'are', 'have', 'has', 'had', 'they', 'you', 'we', 'he', 'she',
        'his', 'her', 'their', 'them', 'can', 'will', 'would', 'should', 'could', 'may', 'might', 'do', 'does', 'did'
    }

    # Split text into sentences by punctuation marks
    sentences = re.split(r'[.!?]+', text)

    # Collect keywords from each sentence
    keyword_freq = {}

    for sentence in sentences:
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', sentence.lower())
        words = normalized.split()
        freq = {}
        for word in words:
            if word and word not in stopwords:
                freq[word] = freq.get(word, 0) + 1
        # Take top keywords from this sentence (e.g., top 3)
        top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
        for w, count in top_words:
            keyword_freq[w] = keyword_freq.get(w, 0) + count

    # Sort combined keywords by frequency
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)

    # Return up to max_keywords keywords
    return [w for w, _ in sorted_keywords[:max_keywords]]
