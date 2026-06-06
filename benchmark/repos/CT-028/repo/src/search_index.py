class SearchIndex:
    def __init__(self, terms):
        self.terms = list(terms)

    def search(self, query):
        return [term for term in self.terms if query in term]
