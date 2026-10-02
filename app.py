import streamlit as st
import requests
import json
from pathlib import Path
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NEXORA AI",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# CONFIG
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

HISTORY_FILE = Path(__file__).parent / "conversations.json"


# =========================================================
# LOAD ALL CONVERSATIONS
# =========================================================

def load_conversations():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    return data

    except Exception:
        pass

    return []


# =========================================================
# SAVE ALL CONVERSATIONS
# =========================================================

def save_conversations(conversations):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                conversations,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as e:
        st.error(f"Could not save history: {e}")
        return False


# =========================================================
# CREATE NEW CHAT
# =========================================================

def create_new_chat():
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "title": "New Conversation",
        "messages": [],
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


# =========================================================
# SESSION STATE
# =========================================================

if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()

if "active_chat" not in st.session_state:

    if st.session_state.conversations:
        st.session_state.active_chat = (
            st.session_state.conversations[-1]["id"]
        )

    else:
        new_chat = create_new_chat()

        st.session_state.conversations.append(new_chat)

        st.session_state.active_chat = new_chat["id"]

        save_conversations(
            st.session_state.conversations
        )


# =========================================================
# GET ACTIVE CHAT
# =========================================================

def get_active_chat():

    for chat in st.session_state.conversations:

        if chat["id"] == st.session_state.active_chat:
            return chat

    # Safety fallback
    new_chat = create_new_chat()

    st.session_state.conversations.append(new_chat)

    st.session_state.active_chat = new_chat["id"]

    save_conversations(
        st.session_state.conversations
    )

    return new_chat


# =========================================================
# OLLAMA
# =========================================================

def ask_ollama(question):

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": question,
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:

            data = response.json()

            return data.get(
                "response",
                "No response received."
            ).strip()

        return f"Ollama Error: {response.status_code}"

    except requests.exceptions.ConnectionError:

        return (
            "Cannot connect to Ollama. "
            "Please make sure Ollama is running."
        )

    except Exception as e:

        return f"Error: {e}"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚡ NEXORA AI")

    st.caption(
        "INTELLIGENCE. PRIVATE. LOCAL."
    )

    st.divider()

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        new_chat = create_new_chat()

        st.session_state.conversations.append(
            new_chat
        )

        st.session_state.active_chat = new_chat["id"]

        save_conversations(
            st.session_state.conversations
        )

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    st.subheader("Conversation History")

    if st.session_state.conversations:

        # Show newest first
        for chat in reversed(
            st.session_state.conversations
        ):

            messages = chat.get(
                "messages",
                []
            )

            # Find first user question
            first_question = None

            for message in messages:

                if message.get("role") == "user":

                    first_question = message.get(
                        "content",
                        "Conversation"
                    )

                    break

            # Display title
            if first_question:

                title = first_question

                if len(title) > 28:
                    title = title[:28] + "..."

            else:

                title = "New Conversation"

            # Active chat indicator
            if chat["id"] == st.session_state.active_chat:

                button_text = f"🟢 {title}"

            else:

                button_text = f"💬 {title}"

            if st.button(
                button_text,
                key=f"chat_{chat['id']}",
                use_container_width=True
            ):

                st.session_state.active_chat = chat["id"]

                st.rerun()

    else:

        st.info("No conversations yet.")

    st.divider()

    # -----------------------------------------------------
    # DELETE ALL HISTORY
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear All History",
        use_container_width=True
    ):

        st.session_state.conversations = []

        new_chat = create_new_chat()

        st.session_state.conversations.append(
            new_chat
        )

        st.session_state.active_chat = new_chat["id"]

        save_conversations(
            st.session_state.conversations
        )

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # SYSTEM STATUS
    # -----------------------------------------------------

    st.subheader("System Status")

    try:

        status = requests.get(
            "http://localhost:11434/api/tags",
            timeout=3
        )

        if status.status_code == 200:

            st.success("● Ollama Online")

        else:

            st.error("● Ollama Offline")

    except Exception:

        st.error("● Ollama Offline")

    st.divider()

    st.write("**Model**")
    st.code(MODEL_NAME)

    st.write("**Runtime**")
    st.caption("Ollama")

    st.write("**Inference**")
    st.caption("100% Local")


# =========================================================
# ACTIVE CHAT
# =========================================================

active_chat = get_active_chat()

messages = active_chat["messages"]


# =========================================================
# MAIN HEADER
# =========================================================

st.title("⚡ NEXORA AI")

st.subheader(
    "Intelligence. Private. Local."
)

st.write(
    "A lightweight local AI assistant powered by "
    "Ollama and Qwen2.5 0.5B."
)

st.divider()


# =========================================================
# EMPTY CHAT
# =========================================================

if not messages:

    st.header(
        "Welcome to NEXORA AI"
    )

    st.write(
        "Ask a question below to start your "
        "local AI conversation."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "🔒 Private by Design\n\n"
            "Your conversation stays on your computer."
        )

    with col2:

        st.info(
            "⚡ Local Inference\n\n"
            "Powered by Qwen2.5 through Ollama."
        )


# =========================================================
# DISPLAY CURRENT CHAT
# =========================================================

else:

    st.header(
        active_chat.get(
            "title",
            "Conversation"
        )
    )

    for message in messages:

        if message["role"] == "user":

            with st.chat_message("user"):

                st.write(
                    message["content"]
                )

        elif message["role"] == "assistant":

            with st.chat_message("assistant"):

                st.write(
                    message["content"]
                )


# =========================================================
# CHAT INPUT
# =========================================================

user_input = st.chat_input(
    "Ask NEXORA AI anything..."
)


# =========================================================
# PROCESS MESSAGE
# =========================================================

if user_input:

    # -----------------------------------------------------
    # First question becomes chat title
    # -----------------------------------------------------

    if not messages:

        active_chat["title"] = user_input

    # -----------------------------------------------------
    # Save USER message
    # -----------------------------------------------------

    active_chat["messages"].append(
        {
            "role": "user",
            "content": user_input
        }
    )

    save_conversations(
        st.session_state.conversations
    )

    # -----------------------------------------------------
    # Generate AI response
    # -----------------------------------------------------

    with st.spinner(
        "⚡ NEXORA AI is thinking..."
    ):

        answer = ask_ollama(
            user_input
        )

    # -----------------------------------------------------
    # Save AI response
    # -----------------------------------------------------

    active_chat["messages"].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    save_conversations(
        st.session_state.conversations
    )

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "NEXORA AI • Ollama • Qwen2.5 0.5B • "
    "Local Inference"
)