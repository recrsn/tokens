from typing import Dict, Set

from tokens.services.token import Token


class TokenStorage:
    tokens: Dict[str, Token] = {}
    available: Set[str] = set()

    def get(self, token_id: str):
        return self.tokens.get(token_id)

    def add(self, token: Token):
        token_id = token.id
        self.tokens[token_id] = token
        self.available.add(token_id)

    def assign(self):
        if not len(self.available):
            return None

        token_id = self.available.pop()
        token = self.tokens[token_id]
        token.allocated = True

        return token

    def unassign(self, token_id: str):
        if token_id in self.tokens:
            token = self.tokens[token_id]
            token.allocated = False
            self.available.add(token_id)

    def delete(self, token_id: str):
        if token_id in self.tokens:
            del self.tokens[token_id]
            self.available.remove(token_id)
