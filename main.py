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
                message_placeholder.write(assistant_response)
                # Add assistant response to chat history
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
        application_token="AstraCS:tKnZHgecDdRdvMdihJMcrqhI:2708b1c53f56ba0f9d6c6e526f026abd7b60746af3b71dfe15b385c06b9979d0"
    )
    print("#################")
    print(prompt)
    print(response['outputs'][0]['outputs'][0]['results']['message']['data']['text'])
    print("#################")
    try:
        # logging.info(f"answer: {response['result']['answer']}")
        return response['outputs'][0]['outputs'][0]['results']['message']['data']['text']
        # return json.dumps(response, indent=2)
    except Exception as exc:
        # logging.error(f"error: {response}")
        return "Sorry, there was a problem finding an answer for you."

if __name__ == "__main__":
    main()
