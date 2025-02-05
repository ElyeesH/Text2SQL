from mistralai import Mistral


class Codestral:
    def __init__(self, key):
        self.client=Mistral(api_key=key)
        self.model='codestral-latest'
    def __call__(self, prompt):
        response=self.client.chat.complete(model=self.model,
                                           temperature=0,
                                            messages=[{"role":"system","content":"You are a helpful AI assistant."},
                                                          {"role":"user","content":prompt}])
        return response.choices[0].message.content

