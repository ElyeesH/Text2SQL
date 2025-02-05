from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
import re

class Deepseek:
    def __init__(self, key, endpoint):
        
        self.client=AzureOpenAI(api_key=key,
                                api_version="2024-05-01-preview",
                                azure_endpoint=endpoint)

        self.deployment_name='DeepSeek-R1'
    def __call__(self, prompt):
        response=self.client.chat.completions.create(model=self.deployment_name,
                                                temperature=0,
                                                messages=[{"role":"system","content":"You are a helpful AI assistant."},
                                                          {"role":"user","content":prompt}])
        response = re.sub(r"<think>.*?</think>\s*", "", response.choices[0].message.content, flags=re.DOTALL)
        return response
    

