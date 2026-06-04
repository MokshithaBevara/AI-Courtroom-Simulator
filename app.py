import os
import streamlit as st
from ddgs import DDGS
from groq import Groq

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="AI Courtroom Simulator",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ AI Courtroom Simulator")
st.write("A multi-agent debate system with live evidence and AI judge verdict.")

# =========================
# API KEY (SAFE)
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# =========================
# LLM CALL FUNCTION
# =========================

def generate_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=300
    )
    return response.choices[0].message.content


# =========================
# LIVE SEARCH TOOL
# =========================

def live_search(query):
    results_text = ""

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

        for r in results:
            results_text += f"""
Title: {r['title']}
Snippet: {r['body']}
Source: {r['href']}

"""

    return results_text


# =========================
# PROSECUTION AGENT
# =========================

def pro_agent(claim, evidence):
    prompt = f"""
You are a PROSECUTION lawyer.

Your job is ONLY to support the statement.

Statement:
{claim}

Evidence:
{evidence}

Provide:
- Strong supporting arguments
- Real-world reasoning
- Conclusion
"""
    return generate_response(prompt)


# =========================
# DEFENSE AGENT
# =========================

def con_agent(claim, evidence):
    prompt = f"""
You are a DEFENSE lawyer.

Your job is ONLY to oppose the statement.

Statement:
{claim}

Evidence:
{evidence}

Provide:
- Counter arguments
- Logical reasoning
- Conclusion
"""
    return generate_response(prompt)


# =========================
# JUDGE AGENT
# =========================

def judge_agent(claim, pro, con):
    prompt = f"""
You are an unbiased judge.

Evaluate both arguments.

Statement:
{claim}

PRO:
{pro}

CON:
{con}

Return:
- Analysis
- Winner
- Final verdict
"""
    return generate_response(prompt)


# =========================
# UI
# =========================

claim = st.text_input(
    "Enter a courtroom statement:",
    "AI will replace programmers by 2030"
)

if st.button("⚖️ Start Courtroom Debate"):

    with st.spinner("🌐 Fetching live evidence..."):
        evidence = live_search(claim)

    with st.spinner("🧠 Running prosecution & defense agents..."):
        pro = pro_agent(claim, evidence)
        con = con_agent(claim, evidence)

    with st.spinner("⚖️ Judge is evaluating..."):
        verdict = judge_agent(claim, pro, con)

    # =========================
    # OUTPUT DISPLAY
    # =========================

    st.divider()

    st.subheader("🌐 Live Evidence")
    st.info(evidence)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 Prosecution")
        st.success(pro)

    with col2:
        st.subheader("🔴 Defense")
        st.error(con)

    st.divider()

    st.subheader("⚖️ Final Verdict")
    st.warning(verdict)
