# ai_agent/graph.py

from datetime import datetime
from typing import Dict
from langgraph.graph import StateGraph, START, END
from state import GroupState   # assuming state.py is next to this file
from tex import tex_optimize
from risk import calculate_risk_scores
from warnings import evaluate_warnings
from onchain_logic import onchain_node
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM Initialization with fallback
llm = None
llm_governance = None

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.6)   # updated model name (2025/2026 naming)
except Exception as e:
    logger.warning(f"Google Gemini init failed: {e}")

try:
    llm_governance = ChatGroq(model="llama3-8b-8192", temperature=0.7)
except Exception as e:
    logger.warning(f"Groq Llama init failed: {e}")

# Fallback if both fail
if llm is None:
    logger.error("No usable LLM available for explanation node")
if llm_governance is None:
    logger.error("No usable LLM available for governance node")

# ────────────────────────────────────────────────
# Nodes
# ────────────────────────────────────────────────

def compute_balances(state: GroupState) -> GroupState:
    balances: Dict[str, float] = {m["user_id"]: 0.0 for m in state["members"]}

    for expense in state.get("expenses", []):
        payer = expense["paid_by"]
        amount = expense["amount"]
        if len(state["members"]) == 0:
            continue
        split_amount = amount / len(state["members"])

        for member in state["members"]:
            uid = member["user_id"]
            if uid == payer:
                balances[uid] += amount - split_amount
            else:
                balances[uid] -= split_amount

    state["balances"] = balances
    state["last_updated"] = datetime.now()
    return state


def tex_node(state: GroupState) -> GroupState:
    # Assuming tex_optimize returns list of settlement dicts
    settlements = tex_optimize(state.get("balances", {}))
    state["pending_settlements"] = settlements   # ← using consistent key from your state schema
    state["last_updated"] = datetime.now()
    return state


def risk_node(state: GroupState) -> GroupState:
    # Placeholder – replace with real DB fetch later
    payment_history = {}
    warning_history = {}
    settlement_history = {}

    state["risk_scores"] = calculate_risk_scores(
        balances=state.get("balances", {}),
        payment_history=payment_history,
        warning_history=warning_history,
        settlement_history=settlement_history
    )
    state["last_updated"] = datetime.now()
    return state


def warning_node(state: GroupState) -> GroupState:
    existing_counts = state.get("warning_counts", {})

    warning_levels, updated_counts, enforcement_flags = evaluate_warnings(
        risk_scores=state.get("risk_scores", {}),
        existing_warning_counts=existing_counts,
        balances=state.get("balances", {})
    )

    state["warning_levels"] = warning_levels
    state["warning_counts"] = updated_counts
    state["excluded_members"] = [
        uid for uid, enforce in enforcement_flags.items() if enforce
    ]
    state["last_updated"] = datetime.now()
    return state


def explanation_node(state: GroupState) -> GroupState:
    if llm is None:
        state["explanation"] = "Explanation unavailable – LLM not initialized."
        return state

    data = {
        "balances": state.get("balances", {}),
        "pending_settlements": state.get("pending_settlements", []),  # consistent naming
        "risk_scores": state.get("risk_scores", {}),
        "warning_levels": state.get("warning_levels", {}),
        "excluded_members": state.get("excluded_members", []),
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are AlgoSettler's transparent Explanation Engine.
Analyze ONLY the provided data.
Rules:
- Never invent numbers or facts
- Explain settlement logic, risk levels, warnings, exclusions
- For excluded members: describe expected future behavior patterns
- Tone: professional, audit-ready, clear
- Structure: use headings and bullet points"""),
        ("human", f"Data:\n{json.dumps(data, indent=2, default=str)}\n\nGenerate full explanation report.")
    ])

    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["explanation"] = response.content.strip()
    except Exception as e:
        logger.error(f"Explanation LLM failed: {e}")
        state["explanation"] = f"Failed to generate explanation: {str(e)}"

    state["last_updated"] = datetime.now()
    return state


def governance_node(state: GroupState) -> GroupState:
    if llm_governance is None:
        state["governance_actions"] = {}
        return state

    warning_levels = state.get("warning_levels", {})
    balances = state.get("balances", {})
    decisions = {}

    for user_id, level_str in warning_levels.items():
        try:
            level_num = {"LEVEL_3": 3, "LEVEL_2": 2, "LEVEL_1": 1}.get(level_str, 0)

            if level_num < 3:
                decisions[user_id] = {
                    "remove_user": False,
                    "deduct_wallet": False,
                    "amount_to_deduct": 0,
                    "reason": "No enforcement action required"
                }
                continue

            prompt = ChatPromptTemplate.from_messages([
                ("system", """Respond ONLY with valid JSON. No extra text.
Format:
{
  "remove_user": true/false,
  "deduct_wallet": true/false,
  "amount_to_deduct": number,
  "reason": "short reason"
}"""),
                ("human", f"""User: {user_id}
Warning Level: {level_num}
Balance: {balances.get(user_id, 0)}

Rules:
- Level >= 3 → recommend removal
- Negative balance → consider deduction
- amount_to_deduct > 0 or 0""")
            ])

            chain = prompt | llm_governance
            raw = chain.invoke({}).content.strip()

            try:
                parsed = json.loads(raw)
                decisions[user_id] = parsed
            except json.JSONDecodeError:
                decisions[user_id] = {
                    "remove_user": False,
                    "deduct_wallet": False,
                    "amount_to_deduct": 0,
                    "reason": "Invalid LLM response format"
                }

        except Exception as e:
            logger.error(f"Governance failed for {user_id}: {e}")
            decisions[user_id] = {
                "remove_user": False,
                "deduct_wallet": False,
                "amount_to_deduct": 0,
                "reason": f"Error: {str(e)}"
            }

    state["governance_actions"] = decisions
    state["last_updated"] = datetime.now()
    return state


# ────────────────────────────────────────────────
# Graph Builder
# ────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(GroupState)

    workflow.add_node("compute_balances", compute_balances)
    workflow.add_node("tex", tex_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("warnings", warning_node)
    workflow.add_node("explanation", explanation_node)
    workflow.add_node("governance", governance_node)
    workflow.add_node("onchain", onchain_node)

    # Flow
    workflow.add_edge(START, "compute_balances")
    workflow.add_edge("compute_balances", "tex")
    workflow.add_edge("tex", "risk")
    workflow.add_edge("risk", "warnings")

    # After warnings → parallel explanation + governance
    workflow.add_edge("warnings", "explanation")
    workflow.add_edge("warnings", "governance")

    # Both converge to onchain
    workflow.add_edge("explanation", "onchain")
    workflow.add_edge("governance", "onchain")
    workflow.add_edge("onchain", END)

    return workflow.compile()