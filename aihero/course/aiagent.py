"""
AI Agent POC - Groq Tool Calling with Override Logic
=======================================================
Flow:
  1. LLM answers the question using context data (no tool yet)
  2. Tool runs independently to get ground-truth value
  3. Compare LLM answer vs Tool result
     MATCH    → return LLM answer
     MISMATCH → override with tool result
"""

import groq
import json

# ─────────────────────────────────────────────
# 1. INVENTORY DATABASE (ground truth)
# ─────────────────────────────────────────────

INVENTORY_DB = {
    "laptop": {"price": 999.99, "size": "15 inch"},
}

# Context data passed to LLM (can differ from DB to simulate mismatch)
CONTEXT_DATA = {
    "laptop": {"price": 20, "size": "15 inch"},
}


# ─────────────────────────────────────────────
# 2. TOOL FUNCTION (ground-truth lookup)
# ─────────────────────────────────────────────

def get_product_price(product_name: str) -> dict:
    """Exact lookup from INVENTORY_DB — this is the source of truth."""
    key = product_name.lower().strip()
    if key in INVENTORY_DB:
        price = INVENTORY_DB[key]["price"]
        return {"found": True, "product": product_name, "price": price}
    return {"found": False, "product": product_name, "price": None}


# ─────────────────────────────────────────────
# 3. TOOL DEFINITION (sent to Groq)
# ─────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "Look up the exact price of a product from the inventory database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to look up"
                    }
                },
                "required": ["product_name"]
            }
        }
    }
]


# ─────────────────────────────────────────────
# 4. COMPARISON HELPER
# ─────────────────────────────────────────────

def llm_answer_matches_tool(llm_answer: str, tool_result: dict) -> bool:
    """Check if the LLM's answer contains the correct price from the tool."""
    if not tool_result.get("found"):
        return False

    price = tool_result["price"]
    answer_lower = llm_answer.lower()

    patterns = [
        str(price),
        f"{price:.2f}",
        f"${price}",
        f"${price:.2f}",
    ]
    return any(p in answer_lower for p in patterns)


# ─────────────────────────────────────────────
# 5. MAIN AGENT
# ─────────────────────────────────────────────

def run_agent(question: str) -> dict:
    client = groq.Groq(api_key="")

    print(f"\n{'='*60}")
    print(f"  QUESTION: {question}")
    print(f"{'='*60}")

    # ── Step 1: LLM answers using context data (NO tool yet) ──
    print("\n[Step 1] LLM answering from context data...")

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a helpful inventory assistant. "
                f"Answer questions using ONLY this context data:\n{json.dumps(CONTEXT_DATA, indent=2)}\n"
                f"Be concise and specific with exact values from the context."
            )
        },
        {"role": "user", "content": question}
    ]

    context_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=256,
        messages=messages          # No tools here — pure context answer
    )
    llm_answer = context_response.choices[0].message.content.strip()
    print(f"  LLM Answer (from context): {llm_answer}")

    # ── Step 2: Run tool independently for ground-truth ──
    print("\n[Step 2] Running tool for ground-truth lookup...")

    # Ask LLM to extract the product name so we can call the tool
    extract_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=64,
        tools=TOOLS,
        tool_choice="auto",    # Force tool call to extract product name
        messages=[
            {"role": "system", "content": "Extract the product name from the question and call the tool."},
            {"role": "user", "content": question}
        ]
    )

    tool_result = None
    extract_message = extract_response.choices[0].message

    if extract_message.tool_calls:
        tool_call = extract_message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        product_name = args.get("product_name", "")

        print(f"  Calling: get_product_price(product_name='{product_name}')")
        tool_result = get_product_price(product_name)
        print(f"  Tool Result: {json.dumps(tool_result, indent=4)}")
    else:
        print("  Could not extract product name for tool call.")

    # ── Step 3: Compare and decide final answer ──
    print("\n[Step 3] Comparing LLM Answer vs Tool Result...")

    if tool_result is None:
        print("  No tool result. Trusting LLM.")
        final_answer = llm_answer
        source = "LLM (unverified)"
        match = None

    elif llm_answer_matches_tool(llm_answer, tool_result):
        print(f"  MATCH — Both agree on price: ${tool_result['price']}")
        final_answer = llm_answer
        source = "LLM (verified by tool)"
        match = True

    else:
        print(f"  MISMATCH — LLM said something different from tool.")
        print(f"  LLM answer  : {llm_answer}")
        print(f"  Tool result : ${tool_result['price']}")
        print(f"  Overriding with tool result.")
        final_answer = f"The price of {tool_result['product'].title()} is ${tool_result['price']:.2f}."
        source = "Tool Override"
        match = False

    print(f"\n[Final Answer] ({source})")
    print(f"  -> {final_answer}")
    print(f"{'='*60}\n")

    return {
        "question": question,
        "llm_answer": llm_answer,
        "tool_result": tool_result,
        "match": match,
        "final_answer": final_answer,
        "source": source
    }


# ─────────────────────────────────────────────
# 6. TEST CASES
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_questions = [
        "What is the price of the laptop?",
    ]

    results = []
    for q in test_questions:
        result = run_agent(q)
        results.append(result)

    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    for r in results:
        status = (
            "MATCH"    if r["match"] is True  else
            "OVERRIDE" if r["match"] is False else
            "NO TOOL"
        )
        print(f"  [{status}] {r['question']}")
        print(f"           Final: {r['final_answer']}\n")