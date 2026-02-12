# Imports
from datetime import datetime
from typing import Dict
from langgraph.graph import StateGraph, START, END
from ai_agent.state import GroupState
from ai_agent.tex import tex_optimize
from ai_agent.risk import calculate_risk_scores
from ai_agent.warnings import evaluate_warnings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Initialising LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6)

# Node 1: Compute Net Balances
def compute_balances(state: GroupState) -> GroupState:
    balances: Dict[str, float] = {}

    # Initialize all members to 0
    for member in state["members"]:
        balances[member["user_id"]] = 0.0

    # Add expenses
    for expense in state["expenses"]:
        payer = expense["paid_by"]
        amount = expense["amount"]

        split_amount = amount / len(state["members"])

        for member in state["members"]:
            user_id = member["user_id"]

            if user_id == payer:
                balances[user_id] += amount - split_amount
            else:
                balances[user_id] -= split_amount

    state["balances"] = balances
    state["last_updated"] = datetime.now()

    return state

# Node 2: TEX Optimization
def tex_node(state: GroupState) -> GroupState:
    state["optimized_settlements"] = tex_optimize(state["balances"])
    return state

# Node 3: Risk Calculation
def risk_node(state: GroupState) -> GroupState:

    # Placeholder histories (replace with DB later)
    payment_history = {}
    warning_history = {}
    settlement_history = {}

    state["risk_scores"] = calculate_risk_scores(
        balances=state["balances"],
        payment_history=payment_history,
        warning_history=warning_history,
        settlement_history=settlement_history
    )

    return state


# Node 4: Warning Evaluation
def warning_node(state: GroupState) -> GroupState:

    # Use existing warning counts from state if available
    existing_warning_counts = state.get("warning_counts", {})

    warning_levels, updated_counts, enforcement_flags = evaluate_warnings(
        risk_scores=state["risk_scores"],
        existing_warning_counts=existing_warning_counts,
        balances=state["balances"]
    )

    # Store results back into state
    state["warning_levels"] = warning_levels
    state["warning_counts"] = updated_counts # Update warning counts in state
    state["excluded_members"] = [
        user_id for user_id, enforce in enforcement_flags.items() if enforce
    ]

    return state

# Node 5: Explanation Generation by LLM
def explanation_node(state: GroupState) -> GroupState:
    """
    Generate natural language explanation using LLM
    """

    balances = state.get("balances", {})
    settlements = state.get("settlements", [])
    risk_scores = state.get("risk_scores", {})
    warning_levels = state.get("warning_levels", {})
    excluded_members = state.get("excluded_members", [])

    structured_data = {
        "balances": balances,
        "settlements": settlements,
        "risk_scores": risk_scores,
        "warning_levels": warning_levels,
        "excluded_members": excluded_members
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are AlgoSettler's Explanation and Reasoning Engine. Your task is to analyze the provided settlement data and generate a clear, 
         logical, and professional explanation for the generated settlements, risk levels, warnings, and any excluded members
based ONLY on the provided JSON data. Also, based on the data of excluded members, generate predictions and analysis as to what type of behavior or patterns should
be expected in the new member(s) added to the group after execution of settlements.

Rules:
- Do NOT change numbers.
- Do NOT invent data.
- Explain why settlements were generated.
- Explain risk levels and warnings.
- Clearly justify excluded members.
- Keep explanation structured and readable.
- Tone: transparent, rational, audit-ready.
- Clearly explain the predictions and analysis for the new member(s).
"""),
        ("human",
         f"""Here is the structured settlement data:

{json.dumps(structured_data, indent=2)}

Generate a complete explanation report.""")
    ])

    chain = prompt | llm

    response = chain.invoke({})

    state["explanation"] = response.content

    return state

# Recommending the member to be removed after LEVEL-3 warning and providing detailed explanation for the same
llm1 = ChatGroq(model="llama3-8b-8192", temperature=0.7)
def governance_node(state: GroupState) -> GroupState:
    """
    This governs the enforcement actions based on warning levels and risk scores. It uses a smaller, faster LLM to make decisions about user removal and wallet deductions.
    """
    warning_levels = state.get("warning_levels", {})
    balances = state.get("balances", {})

    enforcement_decisions = {}

    for user_id, level in warning_levels.items():

        if level >= 3:

            prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
    You are the on-chain connector of AlgoSettler, which provides the insights to the Algorand node for removal of the user who has not
    provided the settlem
    You must strictly follow the decision rules provided.
    You must respond ONLY in valid JSON format.
    Do not add explanations outside JSON.
    Do not include markdown.
    """
            ),
            (
                "human",
                f"""
    User ID: {user_id}
    Warning Level: {level}
    Outstanding Balance: {balances.get(user_id, 0)}

    Rules:
    - If warning level >= 3, recommend removal.
    - If balance < 0, recommend wallet deduction.
    - If no action required, return false for both.
    - amount_to_deduct must be positive number.
    - If no deduction, set amount_to_deduct to 0.

    Respond ONLY in this JSON format:

    {
        "remove_user": true/false,
        "deduct_wallet": true/false,
        "amount_to_deduct": number,
        "reason": "short explanation"
    }
    """
            ),
        ]
    )

            chain = prompt | llm1
            response = chain.invoke({
                "user_id": user_id,
                "level": level,
                "balance": balances.get(user_id, 0)
            })
            try:
                decision = response.content
            except:
                decision = {
                    "remove_user": False,
                    "deduct_wallet": False,
                    "amount_to_deduct": 0,
                    "reason": "Parsing failed"
                }

            enforcement_decisions[user_id] = decision

    state["governance_actions"] = enforcement_decisions

    return state

# Build LangGraph
def build_graph():
    graph = StateGraph(GroupState)
    graph.add_node("compute_balances", compute_balances)
    graph.add_node("tex", tex_node)
    graph.add_node("risk", risk_node)
    graph.add_node("warnings", warning_node)
    graph.add_node("explanation", explanation_node)
    graph.add_node("governance", governance_node)
    graph.add_edge(START, "compute_balances")
    graph.add_edge("compute_balances", "tex")
    graph.add_edge("tex", "risk")
    graph.add_edge("risk", "warnings")
    graph.add_edge("warnings", "explanation")
    graph.add_edge("warnings", "governance")
    graph.add_edge("governance", "onchain_logic") 
    graph.add_edge("onchain_logic", "explanation")
    graph.add_edge("explanation", END)
    return graph.compile()