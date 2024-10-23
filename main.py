import logging
import sys
import time
from typing import Optional
import requests
import json
import streamlit as st
# from streamlit_chat import message
import streamlit as st
from langflow.load import run_flow_from_json
import base64

import toml

with open('secrets.toml', 'r') as f:
    config = toml.load(f)

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "72db4f3e-fa1d-4284-8e2e-0ae9d6bd4f99"
FLOW_ID = "f70e46ce-e1e5-4084-9e11-66aa1c3b1750"
TWEAKS = {
    "APIRequest-oT7rL": {},
    "CreateData-hHbHt": {},
    "CreateData-7JSpN": {},
    "CreateData-QegVy": {},
    "ParseData-biUF9": {},
    "ParseData-Hkhar": {},
    "ChatOutput-9RDag": {},
    "ChatInput-UIN5b": {},
    "MessageToData-5hSnM": {},
    "ParseData-8CCiQ": {},
    "ParseJSONData-CNk8L": {},
    "GetEnvVar-XrtHq": {}
}
ENDPOINT = "test-steamlit" # The endpoint name of the flow

BASE_AVATAR_URL = (
    "https://raw.githubusercontent.com/garystafford-aws/static-assets/main/static"
)

def main():
    st.set_page_config(page_title="Virtual Bartender")
    st.markdown("##### Welcome to the Virtual Bartender")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])
    if prompt := st.chat_input("I'm your virtual bartender, how may I help you?"):
        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "avatar": f"{BASE_AVATAR_URL}/people-64px.png",
            }
        )
        # Display user message in chat message container
        with st.chat_message("user", avatar=f"{BASE_AVATAR_URL}/people-64px.png"):
            st.write(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant",avatar=f"{BASE_AVATAR_URL}/bartender-64px.png"):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt)
                handle_response(message_placeholder, assistant_response)

def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False

def handle_response(message_placeholder, assistant_response):
    b64 = isBase64(assistant_response)
    if b64:
        md = text_to_speech(assistant_response)
        st.markdown(
            md,
            unsafe_allow_html=True,
        )
    else:
        message_placeholder.write(assistant_response)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "avatar": f"{BASE_AVATAR_URL}/bartender-64px.png",
            }
        )



def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    print(message)
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def generate_response(prompt):
    # logging.info(f"{prompt}")
    # inputs = {"question": prompt}
    response = run_flow(prompt,
        endpoint=ENDPOINT,
        tweaks=TWEAKS,
        application_token=config['langflow']['token']
    )
    # print("#################")
    # print(prompt)
    # print(response['outputs'][0]['outputs'][0]['results']['message']['data']['text'])
    # print("#################")
    try:
        # logging.info(f"answer: {response['result']['answer']}")
        return response['outputs'][0]['outputs'][0]['results']['message']['data']['text']
        # return json.dumps(response, indent=2)
    except Exception as exc:
        # logging.error(f"error: {response}")
        return "Sorry, there was a problem finding an answer for you."

def autoplay_audio_url(url: str):
    b64 = base64.b64encode(requests.get(url).content)
    md = f"""
            <audio controls autoplay="true">
            <source src="{url}" type="audio/mp3">
            </audio>
            """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )
def text_to_speech(b64):
    source_type = "audio/flac"
    md = f"""
            <audio controls autoplay="true">
            <source src="data:{source_type};base64,{b64}" type="{source_type}">
            </audio>
            """
    return md

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
