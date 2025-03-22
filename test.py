import ollama
import os
ollama_host = os.environ.get("OLLAMA_HOST", None)
print(ollama_host)
client = ollama.Client(host=ollama_host)

print(client.list())
res=client.chat(model="llama3.1",messages=[{"role":"user","content":"你好，你是谁？"}])
print(res)