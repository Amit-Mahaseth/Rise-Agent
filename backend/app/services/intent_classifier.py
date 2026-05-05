import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentResult:
    intent: str
    confidence: float


class IntentClassifier:
    """
    Lightweight, low-latency intent classifier.

    Design goals:
    - rule-based (cheap) for production cost control
    - deterministic precedence for key intents
    - output a single intent + confidence for strategy routing
    """

    _NOT_INTERESTED = (
        "not interested",
        "dont call",
        "don't call",
        "stop calling",
        "already taken",
        "wrong number",
        "no thanks",
        "no need",
    )
    _CALLBACK_LATER = (
        "call later",
        "call back",
        "callback",
        "tomorrow",
        "later",
        "after some time",
        "next week",
        "day after",
        "i will call",
    )
    _PRICING = (
        "rate",
        "interest rate",
        "emi",
        "monthly",
        "tenure",
        "cost",
        "charges",
        "fees",
        "expensive",
        "how much",
        "pricing",
    )
    _OBJECTION = (
        "expensive",
        "fraud",
        "safe",
        "genuine",
        "risk",
        "not sure",
        "concern",
        "eligibility",
        "cibil",
        "rejected",
    )
    _INTERESTED = (
        "interested",
        "apply",
        "documents",
        "what documents",
        "send link",
        "send me the link",
        "eligible",
        "how soon",
        "call me today",
        "need loan",
        "loan amount",
        "i want",
        "i would like",
    )
    _CONFUSED = (
        "confused",
        "don't understand",
        "dont understand",
        "what is",
        "how does",
        "explain",
        "can you explain",
        "details",
        "what should",
    )

    # Greeting noise sometimes shows up in STT; keep intent robust.
    _STOPWORDS = ("um", "uh", "hello", "hi", "please")

    def classify(self, text: str) -> IntentResult:
        cleaned = self._normalize(text)

        if any(p in cleaned for p in self._NOT_INTERESTED):
            return IntentResult(intent="not_interested", confidence=0.9)

        if any(p in cleaned for p in self._CALLBACK_LATER):
            return IntentResult(intent="callback_later", confidence=0.78)

        if any(p in cleaned for p in self._OBJECTION):
            # Objection can overlap with pricing; give it priority only when explicit.
            confidence = 0.75 if "not sure" in cleaned or "risk" in cleaned or "fraud" in cleaned else 0.62
            return IntentResult(intent="objection", confidence=confidence)

        if any(p in cleaned for p in self._PRICING):
            return IntentResult(intent="pricing", confidence=0.7)

        if any(p in cleaned for p in self._INTERESTED):
            return IntentResult(intent="interested", confidence=0.75)

        if any(p in cleaned for p in self._CONFUSED):
            return IntentResult(intent="confused", confidence=0.66)

        # Fallback: conservative, treat as confused/qualification.
        return IntentResult(intent="confused", confidence=0.45)

    def _normalize(self, text: str) -> str:
        t = (text or "").strip().lower()
        for w in self._STOPWORDS:
            t = t.replace(w, " ")
        t = re.sub(r"\s+", " ", t)
        return t

