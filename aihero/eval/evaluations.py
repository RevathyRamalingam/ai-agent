import os
os.environ['LOGS_DIRECTORY'] = '../eval_logs'

import sys
sys.path.insert(0, '..')
import json
import pandas as pd
import asyncio

from tqdm.auto import tqdm
from pydantic import BaseModel
from pydantic_ai import Agent

from project.logs import LOG_DIR

evaluation_prompt = """
Use this checklist to evaluate the quality of an AI agent's answer (<ANSWER>) to a user question (<QUESTION>).
We also include the entire log (<LOG> for analysis.

For each item, check if the condition is met. 

Checklist:

- instructions_follow: The agent followed the user's instructions (in <INSTRUCTIONS>)
- instructions_avoid: The agent avoided doing things it was told not to do  
- answer_relevant: The response directly addresses the user's question  
- answer_clear: The answer is clear and correct  
- answer_citations: The response includes proper citations or sources when required  
- completeness: The response is complete and covers all key aspects of the request
- tool_call_search: Is the search tool invoked? 

Output your evaluation as a JSON object with this exact format:
{
  "instructions_follow": true,
  "instructions_avoid": true,
  "answer_relevant": true,
  "answer_clear": true,
  "answer_citations": true,
  "completeness": true,
  "tool_call_search": true,
  "summary": "Brief summary of the evaluation"
}

Provide only the JSON output, no additional text.
"""

user_prompt_format = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()

eval_agent = Agent(
    name='eval_agent',
    model='gpt-4o-mini',
    instructions=evaluation_prompt
)

def load_log_file(log_file):
    with open(log_file, 'r') as f_in:
        log_data = json.load(f_in)
        log_data['log_file'] = log_file
        return log_data


def simplify_log_messages(messages):
    log_simplified = []

    for m in messages:
        parts = []
    
        for original_part in m['parts']:
            part = original_part.copy()
            kind = part['part_kind']
    
            if kind == 'user-prompt':
                del part['timestamp']
            if kind == 'tool-call':
                del part['tool_call_id']
            if kind == 'tool-return':
                del part['tool_call_id']
                del part['metadata']
                del part['timestamp']
            if kind == 'tool-return':
                part['content'] = 'RETURN_RESULTS_REDACTED'
            if kind == 'text':
                del part['id']
    
            parts.append(part)
    
        message = {
            'kind': m['kind'],
            'parts': parts
        }
    
        log_simplified.append(message)
    return log_simplified

async def evaluate_log_record(eval_agent, log_record):
    messages = log_record['messages']
    
    instructions = log_record['system_prompt']
    question = messages[0]['parts'][0]['content']
    answer = messages[-1]['parts'][0]['content']
    
    log_simplified = simplify_log_messages(messages)
    log = json.dumps(log_simplified)

    user_prompt = user_prompt_format.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=log
    )

    result = await eval_agent.run(user_prompt)
    response_text = result.output
    
    # Parse JSON from response
    try:
        # Try to extract JSON if wrapped in markdown code blocks
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()
        
        eval_result = json.loads(json_str)
        return eval_result
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON: {e}")
        print(f"Response: {response_text[:200]}")
        return None

async def main():
    print(f"Logs directory: {LOG_DIR.absolute()}")
    
    print("Loading evaluation set...")
    eval_set = []
    
    for log_file in LOG_DIR.glob('*.json'):
        if 'gh_agent' not in log_file.name:
            continue
    
        log_record = load_log_file(log_file)
        if log_record.get('source') != 'ai-generated':
            continue
    
        eval_set.append(log_record)
    
    print(f"Found {len(eval_set)} log files to evaluate")
    
    if len(eval_set) == 0:
        print("No evaluation files found. Make sure to run data-gen.py first.")
        return
    
    eval_results = []
    
    print("Evaluating logs...")
    for log_record in tqdm(eval_set):
        eval_result = await evaluate_log_record(eval_agent, log_record)
        eval_results.append((log_record, eval_result))
    
    print("Creating results dataframe...")
    rows = []
    
    for log_record, eval_result in eval_results:
        messages = log_record['messages']
    
        row = {
            'file': log_record['log_file'].name,
            'question': messages[0]['parts'][0]['content'],
            'answer': messages[-1]['parts'][0]['content'],
        }
    
        # Handle the evaluation result
        if eval_result and isinstance(eval_result, dict):
            # Extract boolean checks (all keys except 'summary')
            for key, value in eval_result.items():
                if key != 'summary' and isinstance(value, bool):
                    row[key] = value
        else:
            print(f"Warning: Could not parse eval result for {row['file']}")
    
        rows.append(row)
    
    df_evals = pd.DataFrame(rows)
    print("\nEvaluation Results:")
    print(df_evals)
    
    # Calculate and display mean scores for boolean columns
    bool_columns = [col for col in df_evals.columns if df_evals[col].dtype == 'bool']
    if bool_columns:
        print("\nMean scores (%):")
        for col in bool_columns:
            score = df_evals[col].mean() * 100
            print(f"{col:25s} {score:6.1f}")
    
    # Save results
    output_file = LOG_DIR / 'evaluation_results.csv'
    df_evals.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())