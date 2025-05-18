from typing import Dict, List

class Prompts:
    base_prompt = """
            # Role
            You are a helpful assistant that can answer questions and help with tasks.
        """

    def format_prompt(self, request: str, context: str = None) -> List[Dict]:
        return [
            {
                "role": "system",
                "content": f"{self.base_prompt}"
            },
            {
                "role": "user",
                "content": f"Customer message: {request}" + (f"\n\nContext: {context}" if context else "")
            }
        ]

