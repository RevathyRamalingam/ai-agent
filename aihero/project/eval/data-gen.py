import os
os.environ['LOGS_DIRECTORY'] = '../eval_logs'

import sys
sys.path.insert(0, '..')
import json
import random
import asyncio

from tqdm.auto import tqdm
from pydantic import BaseModel
from pydantic_ai import Agent

from main import initialize_index, initialize_agent
from logs import log_interaction_to_file, LOG_DIR

question_generation_prompt = """
You are helping to create test questions for an AI agent that answers questions about a data engineering course.

Based on the provided FAQ content, generate realistic questions that students might ask.

The questions should:

- Be natural and varied in style
- Range from simple to complex
- Include both specific technical questions and general course questions

Generate one question for each record.
""".strip()

class QuestionsList(BaseModel):
    questions: list[str]

question_generator = Agent(
    name="question_generator",
    instructions=question_generation_prompt,
    model='gpt-4o-mini'
)

async def main():
    print(f"Logs will be saved to: {LOG_DIR.absolute()}")
    
    print("Initializing index...")
    index = initialize_index()
    
    print("Initializing agent...")
    agent = initialize_agent(index)
    
    print("Sampling documents and generating questions...")
    sample = random.sample(index.docs, 10)
    prompt = [d['content'] for d in sample]
    
    print("Generating questions from sampled content...")
    result = await question_generator.run(user_prompt=json.dumps(prompt))
    
    # Parse the response (it will be text, not structured data)
    response_text = result.data if hasattr(result, 'data') else str(result)
    
    # Split the response into individual questions
    # Assuming each question is on a new line or numbered
    questions = [q.strip() for q in response_text.split('\n') if q.strip() and not q.strip().startswith('#')]
    questions = [q.lstrip('0123456789.-) ') for q in questions if len(q.strip()) > 10]
    
    print(f"\nGenerated {len(questions)} questions. Processing...\n")
    
    for question in tqdm(questions):
        print(f"\nQuestion: {question}")
        result = await agent.run(user_prompt=question)
        answer = result.data if hasattr(result, 'data') else str(result)
        print(f"Answer: {answer}")
        log_interaction_to_file(agent, result.new_messages(), source='ai-generated')
        print()

if __name__ == "__main__":
    asyncio.run(main())