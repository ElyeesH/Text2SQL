"""from groq import Groq

client = Groq(
    api_key='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',
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)"""


"""api_key='lPiTURZibUI12Uc8FtmMwaxc73pSkeTJ'

from mistralai import Mistral

model = "codestral-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
print(chat_response.choices[0].message.content)"""



api_token='xaD6cj77fr_6qwWZqoLQd1UNpuAPJj_9GFsZGTKy'

import requests

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/7a28da0b7bb01cbc27b1da34372b86ea/ai/run/"
headers = {"Authorization": "Bearer xaD6cj77fr_6qwWZqoLQd1UNpuAPJj_9GFsZGTKy"}

def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()

inputs = [
    { "role": "system", "content": "You are a friendly assistant" },
    { "role": "user", "content": """Answer the question by SQLite SQL query only and with no explanation . You must minimize SQL execution time while ensuring correctness .
 ### Sqlite SQL tables , with their properties :
 #
 # singer ( Singer_ID ,Name , Country , Song_Name , Song_release_year ,Age ,Is_male );
 # singer_in_concert ( concert_ID , Singer_ID );
 #
 ### Here is some data information about database references .
 #
# singer ( Singer_ID [1 ,2 ,3] , Name [Joe , Timbaland , Justin Brown ] , Country [Netherlands , United States , France ] , Song_Name [You , Dangerous ,Hey Oh] ,

Song_release_year [1992 ,2008 ,2013] , Age [52 ,32 ,29] , Is_male [F,T,T]);
 # singer_in_concert ( concert_ID [1 ,1 ,1] , Singer_ID [2 ,3 ,5]) ;
 #
 ### Foreign key information of SQLite tables , used for table joins :
#
 # singer_in_concert ( Singer_ID ) REFERENCES singer ( Singer_ID );
#
### Question : How many singers do we have ?
 ### SQL :
"""}
]
output = run("@cf/defog/sqlcoder-7b-2", inputs)
print(output['result']['response'])