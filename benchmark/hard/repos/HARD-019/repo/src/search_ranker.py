from datetime import datetime, timezone


def rank_results(query, documents):
    terms = [term.casefold() for term in query.split() if term.strip()]

    def timestamp(document):
        value = document.get("updated_at")
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def score(document):
        haystack = f"{document.get('title', '')} {document.get('body', '')}".casefold()
        return sum(1 for term in terms if term in haystack)

    indexed = list(enumerate(documents))
    indexed.sort(
        key=lambda item: (
            score(item[1]),
            timestamp(item[1]),
            -item[0],
        ),
        reverse=True,
    )
    return [document for _, document in indexed]
