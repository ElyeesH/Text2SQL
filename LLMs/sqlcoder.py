import requests


class SQLCoder:
    def __init__(self, token, id):
        self.model='@cf/defog/sqlcoder-7b-2'
        self.headers={"Authorization":f"Bearer {token}"}
        self.url=f"https://api.cloudflare.com/client/v4/accounts/{id}/ai/run/"
    def __call__(self, prompt):
        input = { "messages": [{"role": "system", "content": "You are a friendly assistant"},
                                {"role": "user", "content": prompt}]}
        response=requests.post(self.url, headers=self.headers,json=input)
        print(response.json())
        return response.json()['result']['response']
    

sqlcoder=SQLCoder("","")  # cloudflare token
print(sqlcoder('hello'))