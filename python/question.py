import streamlit as st
import requests
import random
import os
import json
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"   # disabled — no valid API key

# ---------------------------
# Streamlit page setup
# ---------------------------
st.set_page_config(page_title="Practice Mode - TECCY", layout="centered", page_icon="🎮")

# ---------------------------
# Theme CSS (Stardew Valley)
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jersey+10&display=swap');
* { font-family: 'Jersey 10', sans-serif !important; }

.stApp {
    background-color: #69a74e !important;
    background-image:
        radial-gradient(#7bc65d 15%, transparent 16%),
        radial-gradient(#5d9e43 15%, transparent 16%) !important;
    background-size: 60px 60px !important;
    background-position: 0 0, 30px 30px !important;
    color: #4a2f1b !important;
}
.main .block-container {
    background-color: #ffcca8;
    border: 4px solid #5e3a23;
    border-radius: 12px;
    box-shadow: inset 0 0 0 4px #e09f6d, 8px 8px 0 rgba(0,0,0,0.4);
    padding: 2rem !important;
    max-width: 90% !important;
    margin-top: 2rem;
}
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #4a2f1b !important;
    border-color: #5e3a23 !important;
}
h1 {
    font-size: 2.8rem !important;
    color: #a43322 !important;
    text-shadow: 2px 2px 0 #ffcca8 !important;
    border-bottom: 2px solid #5e3a23 !important;
    text-align: center;
}
p, span, label, .stMarkdown, .stText {
    font-size: 1.2rem !important;
    color: #4a2f1b !important;
}
section[data-testid="stSidebar"] {
    background-color: #ffd400 !important;
    border-right: 4px solid #5e3a23 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #5e3a23 !important;
    text-shadow: 1px 1px 0 #e09f6d !important;
}
section[data-testid="stSidebar"] .stMarkdown a {
    display: block;
    background-color: #fff192;
    border: 2px solid #5e3a23 !important;
    color: #4a2f1b !important;
    padding: 10px;
    text-align: center;
    border-radius: 6px;
    box-shadow: 2px 2px 0 rgba(0,0,0,0.4);
    margin: 5px 0;
}
.stButton > button {
    background-color: #d95d45 !important;
    color: #fff !important;
    border: 2px solid #5e3a23 !important;
    border-radius: 4px !important;
    padding: 10px 16px !important;
    box-shadow: 0 4px 0 #9e2b1e !important;
    font-size: 1.2rem !important;
    transition: all 100ms !important;
}
.stButton > button:hover {
    background-color: #ff7e60 !important;
    transform: translateY(2px) !important;
    box-shadow: 0 2px 0 #9e2b1e !important;
}
.stButton > button:active {
    transform: translateY(4px) !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input, .stSelectbox > div > div {
    background-color: #ffffff !important;
    border: 2px solid #5e3a23 !important;
    color: #4a2f1b !important;
    border-radius: 4px !important;
    box-shadow: 2px 2px 0 rgba(0,0,0,0.4) !important;
}
.stSuccess { background-color: #e8f5e9 !important; border: 2px solid #5e3a23 !important; color: #4a2f1b !important; }
.stError   { background-color: #ffebee !important; border: 2px solid #e63e3e !important; color: #4a2f1b !important; }
.stInfo    { background-color: #fff192 !important; border: 2px solid #5e3a23 !important; color: #4a2f1b !important; }
.stWarning { background-color: #fff3e0 !important; border: 2px solid #ff8a00 !important; color: #4a2f1b !important; }
.stMarkdown a { color: #d95d45 !important; text-decoration: underline !important; }
hr { border-color: #5e3a23 !important; opacity: 0.5; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Level-up / reward box */
.levelup-box {
    background: linear-gradient(135deg, #fff192, #ffd400);
    border: 4px solid #5e3a23;
    border-radius: 12px;
    padding: 28px;
    text-align: center;
    box-shadow: 6px 6px 0 rgba(0,0,0,0.35);
    margin: 20px 0;
}
.levelup-box h2 { font-size: 2.2rem !important; color: #a43322 !important; margin-bottom: 8px; }
.levelup-box p  { font-size: 1.3rem !important; }

/* Progress bar track */
.acc-bar-bg {
    background: #e09f6d;
    border: 2px solid #5e3a23;
    border-radius: 6px;
    height: 18px;
    margin-bottom: 6px;
    overflow: hidden;
}
.acc-bar-fill {
    height: 100%;
    background: #d95d45;
    border-radius: 4px;
    transition: width 0.4s;
}
</style>
""", unsafe_allow_html=True)

st.title("// PRACTICE MODE")

# ---------------------------
# URL params
# ---------------------------
topic = st.query_params.get("topic", "Algebra")
level = st.query_params.get("level", "Beginner")
if isinstance(topic, list): topic = topic[0] if topic else "Algebra"
if isinstance(level, list): level = level[0] if level else "Beginner"

# Level ordering
LEVEL_ORDER = ["AMATEUR", "INTERMEDIATE", "ADVANCED", "PRO"]

def next_level(lvl: str):
    lvl_up = lvl.upper()
    if lvl_up in LEVEL_ORDER:
        idx = LEVEL_ORDER.index(lvl_up)
        if idx < len(LEVEL_ORDER) - 1:
            return LEVEL_ORDER[idx + 1]
    return None  # already at top

# ---------------------------
# Session state initialisation
# ---------------------------
if "current_level" not in st.session_state:
    st.session_state["current_level"] = level.upper()

if "q_count" not in st.session_state:           # questions in current 10-block
    st.session_state["q_count"] = 0
if "correct_count" not in st.session_state:     # correct answers in current block
    st.session_state["correct_count"] = 0
if "show_levelup" not in st.session_state:      # trigger level-up popup
    st.session_state["show_levelup"] = False
if "levelup_to" not in st.session_state:        # what level the user just reached
    st.session_state["levelup_to"] = ""
if "target_reached" not in st.session_state:   # user reached their target level
    st.session_state["target_reached"] = False
if "target_level" not in st.session_state:
    st.session_state["target_level"] = ""       # filled from URL later

# Derive target level from URL (stored in Supabase but exposed via query param for now)
target_level_param = st.query_params.get("target", "")
if isinstance(target_level_param, list): target_level_param = target_level_param[0]
if target_level_param and not st.session_state["target_level"]:
    st.session_state["target_level"] = target_level_param.upper()

current_lvl = st.session_state["current_level"]

# ---------------------------
# Navigation sidebar
# ---------------------------
st.sidebar.markdown("### [ NAVIGATION ]")
st.sidebar.markdown("[🏠 Back to Homepage](http://localhost:8080/index.html)")
st.sidebar.markdown("---")

# ---------------------------
# Model selector (default phi3 which is installed)
# ---------------------------
st.sidebar.markdown("### [ MODEL SELECT ]")
model_choice = st.sidebar.selectbox("Select Model", ["phi3:3.8b", "llama3.2:1b"], index=0)
st.sidebar.markdown(f"**Active:** `{model_choice}`")
if "phi3" in model_choice:
    st.sidebar.info("🧠 REASON MODE")
else:
    st.sidebar.success("⚡ FAST MODE")

llm = OllamaLLM(model=model_choice, temperature=0.3, num_ctx=2048)

# ---------------------------
# Progress display
# ---------------------------
q_in_block  = st.session_state["q_count"]
ok_in_block = st.session_state["correct_count"]
acc_pct     = int((ok_in_block / q_in_block * 100)) if q_in_block > 0 else 0
remaining   = 10 - q_in_block

st.markdown(f"**TOPIC:** {topic.upper()} | **LEVEL:** {current_lvl}")
st.markdown(
    f"📊 **Block progress:** {ok_in_block}/{q_in_block} correct "
    f"({acc_pct}% accuracy) | 🔢 {remaining} question(s) left in this block"
)
# Draw accuracy bar
st.markdown(
    f'<div class="acc-bar-bg"><div class="acc-bar-fill" style="width:{acc_pct}%;"></div></div>',
    unsafe_allow_html=True
)
st.caption("Need 75%+ over 10 questions to level up 🌱")

# ---------------------------
# 🎉 LEVEL-UP POPUP
# ---------------------------
if st.session_state["show_levelup"]:
    new_lvl  = st.session_state["levelup_to"]
    seed_map = {
        "INTERMEDIATE": ("🌿", "Growth Fertilizer"),
        "ADVANCED":     ("🪴", "Advanced Fertilizer"),
        "PRO":          ("🌳", "Master Fertilizer"),
    }
    icon, seed_name = seed_map.get(new_lvl, ("🌱", "Fertilizer"))

    st.markdown(f"""
    <div class="levelup-box">
        <h2>🎉 LEVEL UP! {new_lvl}</h2>
        <p>You answered with 75%+ accuracy over 10 questions — amazing work!</p>
        <br>
        <p>🎁 <strong>Reward unlocked:</strong></p>
        <!-- PLACEHOLDER: replace the box below with an actual fertilizer image -->
        <div style="width:90px;height:90px;border:3px dashed #5e3a23;border-radius:8px;
                    margin:0 auto 12px;display:flex;align-items:center;justify-content:center;
                    background:#fff8eb;font-size:3rem;">
            {icon}
        </div>
        <p style="font-size:1.4rem;"><strong>{seed_name}</strong></p>
        <p style="opacity:0.8;">Use it in your Greenhouse to boost crops!</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ AWESOME! KEEP GOING"):
        st.session_state["show_levelup"] = False
        st.rerun()
    st.stop()   # don't show rest of UI while popup is visible

# ---------------------------
# 🏆 TARGET LEVEL REACHED
# ---------------------------
if st.session_state["target_reached"]:
    tgt = st.session_state["target_level"] or current_lvl
    st.markdown(f"""
    <div class="levelup-box">
        <h2>🏆 TARGET REACHED: {tgt}</h2>
        <p>You've reached your goal level! What would you like to do next?</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 KEEP PRACTISING"):
            st.session_state["target_reached"] = False
            st.rerun()
    with col2:
        final_url = f"http://localhost:8080/pages/final-test.html?topic={topic}"
        st.markdown(
            f'<a href="{final_url}" target="_blank">'
            f'<button style="background:#d95d45;color:#fff;border:2px solid #5e3a23;'
            f'border-radius:4px;padding:10px 16px;font-size:1.2rem;cursor:pointer;'
            f'box-shadow:0 4px 0 #9e2b1e;font-family:Jersey 10,sans-serif;width:100%;">'
            f'🎯 TAKE FINAL TEST</button></a>',
            unsafe_allow_html=True
        )
    st.stop()

# ---------------------------
# Parse JSON helper (robust — handles markdown fences, extra text, phi3 quirks)
# ---------------------------
def parse_json_output(model_output: str):
    """Try multiple strategies to extract JSON from the model response."""
    if not model_output:
        return None

    text = model_output.strip()

    # Strategy 1: Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)

    # Strategy 2: Direct parse if it looks like JSON already
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Extract first {...} block (handles text before/after JSON)
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        candidate = brace_match.group(0)
        # Fix trailing commas (common phi3 quirk): ,} → }  and ,] → ]
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 4: Line-by-line extraction fallback
    lines = text.splitlines()
    json_lines = []
    in_json = False
    brace_depth = 0
    for line in lines:
        if not in_json and "{" in line:
            in_json = True
        if in_json:
            json_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if in_json and brace_depth <= 0:
                break
    if json_lines:
        candidate = "\n".join(json_lines)
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


# ---------------------------
# Generate Question
# ---------------------------
st.markdown("---")
if st.button("[ GENERATE QUESTION ]"):
    question_prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are an expert math teacher. Generate ONE {level} level math problem from: {topic}.
Respond STRICTLY in this JSON format with NO extra text:
{{
  "question": "full problem statement",
  "answer": "exact correct answer (number or expression)",
  "solution_steps": [
    "Step 1: [explanation]",
    "Step 2: [explanation]",
    "Step 3: [explanation]",
    "... as many steps as needed"
  ],
  "key_concept": "one sentence explanation of the main concept used"
}}
Make the solution_steps very detailed and educational — each step should explain WHY not just WHAT."""
        ),
        ("user", f"Generate a unique {level} {topic} question. Seed: {random.randint(1, 999999)}")
    ])

    chain = question_prompt | llm | StrOutputParser()

    with st.spinner("GENERATING..."):
        try:
            qa_json = chain.invoke({"topic": topic, "level": current_lvl})
        except requests.exceptions.ConnectionError:
            st.error("❌ CONNECTION ERROR: Could not connect to Ollama.")
            st.warning("Make sure Ollama is running: `ollama serve`")
            st.stop()
        except Exception as e:
            st.error(f"❌ ERROR: {e}")
            st.stop()

    qa_data = parse_json_output(qa_json)
    if qa_data:
        st.session_state["current_question"]  = qa_data.get("question", "")
        st.session_state["correct_answer"]    = qa_data.get("answer", "")
        st.session_state["solution_steps"]    = qa_data.get("solution_steps", [])
        st.session_state["key_concept"]       = qa_data.get("key_concept", "")
        st.session_state["answer_checked"]    = False   # reset check state
    else:
        st.error("⚠️ Unexpected response format — try again.")
        st.text(qa_json)

# ---------------------------
# Display Question & Answer
# ---------------------------
if "current_question" in st.session_state:
    st.markdown("---")
    st.subheader("// QUESTION")
    st.write(st.session_state["current_question"])

    user_answer = st.text_input("YOUR ANSWER:", key="user_answer_input")

    if st.button("[ CHECK ANSWER ]") and not st.session_state.get("answer_checked"):
        if not user_answer.strip():
            st.warning("⚠️ Enter an answer first!")
        else:
            correct = str(st.session_state["correct_answer"]).strip().lower()
            given   = user_answer.strip().lower()
            is_correct = given == correct

            # ── Track accuracy ──
            st.session_state["q_count"]     += 1
            if is_correct:
                st.session_state["correct_count"] += 1
            st.session_state["answer_checked"] = True

            # ── Show result ──
            if is_correct:
                st.success("✅ CORRECT! Well done!")
            else:
                st.error(f"❌ WRONG.  Correct answer: **{st.session_state['correct_answer']}**")

            # ── Detailed step-by-step solution ──
            steps = st.session_state.get("solution_steps", [])
            concept = st.session_state.get("key_concept", "")

            if steps:
                st.subheader("// STEP-BY-STEP SOLUTION")
                for i, step in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {step}")
                if concept:
                    st.info(f"💡 **Key Concept:** {concept}")
            else:
                # Fallback: ask the model for a solution if not provided
                st.subheader("// SOLUTION")
                solve_prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     """You are a math teacher. A student got this question wrong.
Give a very detailed, step-by-step solution that teaches WHY each step is done.
Format: numbered list, plain text only, no JSON."""
                    ),
                    ("user",
                     f"Question: {st.session_state['current_question']}\n"
                     f"Correct answer: {st.session_state['correct_answer']}\n"
                     "Explain in full detail."
                    )
                ])
                with st.spinner("Generating detailed solution..."):
                    solution_text = (solve_prompt | llm | StrOutputParser()).invoke({})
                st.write(solution_text)

            # ── Check block completion (every 10 questions) ──
            block_done = st.session_state["q_count"] >= 10
            if block_done:
                block_acc = st.session_state["correct_count"] / 10
                st.markdown("---")
                st.subheader("// BLOCK COMPLETE (10 QUESTIONS)")

                if block_acc >= 0.75:
                    # Level up!
                    nxt = next_level(current_lvl)
                    if nxt:
                        st.session_state["current_level"]  = nxt
                        st.session_state["levelup_to"]     = nxt
                        st.session_state["show_levelup"]   = True

                        # Check if target reached
                        tgt = st.session_state.get("target_level", "")
                        if tgt and nxt == tgt:
                            st.session_state["target_reached"] = True
                            st.session_state["show_levelup"]   = False
                    else:
                        st.success("🏆 You're already at the highest level — PRO!")
                else:
                    st.warning(
                        f"📉 {int(block_acc*100)}% accuracy — need 75% to level up. "
                        f"Keep practising at **{current_lvl}**!"
                    )

                # Reset block counter for next round
                st.session_state["q_count"]     = 0
                st.session_state["correct_count"] = 0

                if not st.session_state["show_levelup"] and not st.session_state["target_reached"]:
                    st.info("▶️ Click **GENERATE QUESTION** for your next block!")
