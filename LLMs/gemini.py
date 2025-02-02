import google.generativeai as genai


class Gemini:
    def __init__(self, key):
        genai.configure(api_key=key, transport="rest")
        self.model=genai.GenerativeModel("gemini-1.5-flash")
    def __call__(self, prompt):
        config = genai.GenerationConfig(
        temperature=0,)
        response=self.model.generate_content(prompt,
                                             generation_config=config)
        return response.text



gemini=Gemini('')  # google api key
print(gemini('hello'))