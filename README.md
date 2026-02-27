📘 Patient Journey Orchestration Agent
Multi-Agent Workflow using LangGraph + LangChain
🚀 Overview

This project implements a stateful, multi-agent orchestration system using LangGraph and LangChain, simulating a real-world patient journey workflow.

The system demonstrates:

Deterministic state transitions

Multi-agent orchestration

Tool-calling via LLM

Retry and escalation control

Stateful workflow loops

Clear separation of reasoning vs execution

The architecture mirrors how production-grade AI systems should be designed.

🧠 Architecture Overview

This system is built using LangGraph’s StateGraph, where each agent is a node in a directed graph.

                ┌──────────────────┐
                │  DependencyAgent │
                └──────────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │  SchedulingAgent │
                └──────────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │   ReminderAgent  │
                └──────────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │  MonitoringAgent │
                └───────┬──────────┘
                        │
            ┌───────────┴────────────┐
            ▼                        ▼
        Continue                  Stop (END)
        (Loop)                     
🏗 Core Concepts Implemented
1️⃣ Stateful Workflow (LangGraph)

The entire system operates on a shared PatientState object.

LangGraph ensures:

Deterministic transitions

Controlled routing

Looping behavior

Clear termination conditions

2️⃣ Canonical Patient State

PatientState is the single source of truth.

It contains:

current_state

history

events

signals

retry_counts

current_time (simulated time)

Patient Journey States
NEW_PATIENT
INTAKE_COMPLETED
APPOINTMENT_SCHEDULED
APPOINTMENT_COMPLETED
LAB_TEST_REQUIRED
LAB_TEST_SCHEDULED
LAB_TEST_COMPLETED
DOCTOR_REVIEW_PENDING
FOLLOW_UP_SCHEDULED
FOLLOW_UP_COMPLETED
JOURNEY_CLOSED

States represent facts, not intentions.

3️⃣ Agents and Responsibilities
🧩 DependencyAgent

Checks preconditions

Does NOT mutate state

Controls entry to scheduling

📅 SchedulingAgent

Decides next desired state

Handles rescheduling logic

Enforces retry limits

Sets escalation signals when max retries reached

Does NOT directly send notifications

⏰ ReminderAgent

Time-aware agent

Detects upcoming events

Detects missed events

Calls tools (email/SMS/call)

Sets workflow signals

Does NOT mutate state

🔍 MonitoringAgent

Decides whether workflow should continue

Halts on:

Terminal states

Escalation signals

No state changes

🔁 Retry & Escalation Logic

Each event type has retry limits:

MAX_RETRIES = {
    "appointment": 2,
    "lab_test": 2,
    "follow_up": 1,
}

If exceeded:

escalation_required signal is set

MonitoringAgent halts workflow

This models real-world operational safeguards.

🛠 Tool Calling (LLM Integration)

The system integrates tool-calling via LangChain:

Tools:

send_email

send_sms

make_call

The LLM:

Decides which tool to call

Produces structured tool calls

Executes external actions

Example pattern:

self.llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

self.llm_with_tools = self.llm.bind_tools(self.tools)

This demonstrates real AI-to-tool execution pipelines.

🕒 Simulated Time Engine

Instead of relying on real system time:

current_time: datetime = datetime(2025, 1, 1, 9, 0)

Benefits:

Deterministic testing

Replayability

Predictable agent behavior

No cron dependency

This models event-driven systems safely.

🧱 Deterministic + LLM Hybrid Design

The system cleanly separates:

Responsibility	Layer
Business rules	Deterministic
State transitions	Validated
Tool execution	Controlled
Decision-making	LLM
Orchestration	LangGraph

This prevents hallucinated state corruption.

📂 Project Structure
app/
 ├── agents/
 │    ├── dependency_agent.py
 │    ├── scheduling_agent.py
 │    ├── reminder_agent.py
 │    ├── monitoring_agent.py
 │
 ├── core/
 │    ├── state.py
 │    ├── validator.py
 │
 ├── tools/
 │    ├── notification_tools.py
 │
 ├── workflows/
 │    ├── patient_journey_graph.py
 │
main.py
🔬 What This Project Demonstrates
✔ Multi-Agent Orchestration

Explicit graph-based routing and loops.

✔ Stateful Workflow Control

Single canonical state object.

✔ LLM Tool Calling

Structured execution through LangChain tools.

✔ Retry & Escalation Safety

Production-inspired resilience patterns.

✔ Deterministic Control + AI Reasoning

Hybrid architecture pattern.
