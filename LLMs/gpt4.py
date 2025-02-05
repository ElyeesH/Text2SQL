from openai import AzureOpenAI


class GPT4:
    def __init__(self, key, endpoint):
        self.client=AzureOpenAI(api_key=key,
                                api_version="2023-05-15",
                                azure_endpoint=endpoint)
        self.deployment_name='gpt-4'
    def __call__(self, prompt):
        response=self.client.chat.completions.create(model=self.deployment_name,
                                                temperature=0,
                                                messages=[{"role":"system","content":"You are a helpful AI assistant."},
                                                          {"role":"user","content":prompt}])
        return response.choices[0].message.content
    
