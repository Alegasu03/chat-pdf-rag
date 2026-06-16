from google import genai


class LLMService:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            return response.text or "No se pudo generar una respuesta."

        except Exception as e:
            print(f"LLM ERROR: {e}")

            return (
                "Ha ocurrido un error al generar la respuesta. "
                "Por favor, inténtalo de nuevo."
            )