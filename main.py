from langflow.load import run_flow_from_json
TWEAKS = {
  "ChatInput-T1x31": {},
  "ChatOutput-N0i2h": {}
}

result = run_flow_from_json(flow="Test LangFlow Streamlit.json",
                            input_value="message",
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)
