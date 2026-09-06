

import re

from chatbot.models import FAQ

FALLBACK_ANSWER = "Sorry, I could not find an answer. Please contact customer support."


def clean_text(text: str) -> str:
    """Lowercase the text and remove punctuation, keeping only words/spaces."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_best_answer(user_message: str) -> str:
    cleaned = clean_text(user_message)
    message_words = set(cleaned.split())

    if not message_words:
        return FALLBACK_ANSWER

    best_answer = None
    best_score = 0

    for faq in FAQ.objects.filter(is_active=True):
        faq_keywords = {
            clean_text(keyword) for keyword in faq.keywords.split(",") if keyword.strip()
        }

        
        score = 0
        for keyword in faq_keywords:
            keyword_words = set(keyword.split())
            if keyword_words and keyword_words.issubset(message_words):
                score += 1

        if score > best_score:
            best_score = score
            best_answer = faq.answer

    return best_answer if best_answer else FALLBACK_ANSWER
