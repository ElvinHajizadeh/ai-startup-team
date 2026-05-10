import g4f

try:
    print("Testing G4F...")
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o_mini,
        messages=[{"role": "user", "content": "Salam, sən kimsən?"}],
    )
    print("Response:", response)
except Exception as e:
    print("Error:", e)
