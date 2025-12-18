import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
print(openai.api_key)

from openai import OpenAI

client = OpenAI()

user_prompt = "I just discovered the course, can I join now?"

chat_messages = [
    {"role": "user", "content": user_prompt}
]


completion = client.responses.create(
    model="gpt-4o-mini",
    input=chat_messages
)

print(completion.output_text)