import streamlit as st
import requests
import uuid
import os

# API Configuration
API_URL = 'https://crypto-analysis-assistant-production.up.railway.app/chat'

def chat_with_api(user_message, history, session_id=None):
    payload = {
        "message": user_message,
        "history": history,
        "session_id": session_id
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return {
            "answer": response.json()["response"],
            "session_id": response.json()["session_id"]
        }
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return {"error": str(e)}

def initialize_session_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}

    
    if not st.session_state.chats:
        create_new_chat()

def create_new_chat():
    new_chat_id = str(uuid.uuid4())
    
    st.session_state.chats[new_chat_id] = {
        "messages": [],
        "api_session_id": None,
        "active": True
    }
    
    st.session_state.current_chat_id = new_chat_id

def delete_chat(chat_id):
    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]
        
        if not st.session_state.chats:
            create_new_chat()
        else:
            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]

def main():
    st.set_page_config(page_title="Crypto Assistant", page_icon="💡")

    initialize_session_state()

    # Sidebar for chat management
    st.sidebar.title("Chat Management")
    st.sidebar.button("New Chat", on_click=create_new_chat)

    # Chat selection in sidebar
    chat_ids = list(st.session_state.chats.keys())
    selected_chat_id = st.sidebar.radio(
        "Select Chat", 
        chat_ids, 
        index=chat_ids.index(st.session_state.current_chat_id),
        format_func=lambda x: f"Chat {chat_ids.index(x) + 1}"
    )

    # Update current chat if selection changes
    if selected_chat_id != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat_id

    # Delete chat button
    if st.sidebar.button("Delete Current Chat"):
        delete_chat(st.session_state.current_chat_id)

    # Main chat interface
    st.title("Crypto Analysis Assistant")
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    messages = current_chat["messages"]

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
        # Message history
        message_history = messages[-10:]
        history = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in message_history]) or " "

        # Display user message
        st.chat_message("user").markdown(prompt)
        
        # Add user message to current chat
        current_chat["messages"].append({"role": "user", "content": prompt})

        # Display loading spinner
        with st.spinner('Thinking...'):
            response = chat_with_api(
                prompt, 
                history, 
                session_id=current_chat.get("api_session_id")
            )
        
        # Handle API response
        if "error" in response:
            st.error("Terjadi kesalahan saat mengambil respon.")
            return

        # Update API session ID if not set
        if not current_chat.get("api_session_id"):
            current_chat["api_session_id"] = response.get("session_id")
        
        answer = response["answer"]
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Add assistant response to current chat
        current_chat["messages"].append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
