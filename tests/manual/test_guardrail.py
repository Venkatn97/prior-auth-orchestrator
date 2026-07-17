from shared.bedrock_client import invoke_claude

result = invoke_claude("My name is John Smith, SSN 123-45-6789, phone 555-123-4567. Summarize this in one sentence.")
print(result)
