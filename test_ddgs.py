from duckduckgo_search import DDGS

try:
    print("Testing DDGS chat...")
    response = DDGS().chat("Salam, sən kimsən və hansı modelsən? Qısa cavab ver.", model="gpt-4o-mini")
    print("Response:", response)
except Exception as e:
    print("Error:", e)
