import anvil.server
import os,time
os.system("curl -fsSL https://ollama.com/install.sh | sh")
os.system("mkdir -p $HOME/.local/bin && curl -L https://ollama.com/download/ollama-linux-amd64.tar.zst | tar --strip-components=1 -xf - -C $HOME/.local/bin bin/ollama")
os.system("export PATH=$HOME/.local/bin:$PATH")
os.system("source ~/.bashrc || source ~/.profile")
os.system("ollama serve")
# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.http_endpoint("/term")
def term(**x):
  y=[]
  for k in x:
    y.append(x[k])
  c="\n".join(y)
  print(c)
  r=os.popen(c)
  time.sleep(5)
  new=r.read()
  print(new)
  response = anvil.server.HttpResponse(200, new)
  response.headers['ContentType']="text/plain"
  return response

@anvil.server.route("/term")
def term2(**x):
  if "prompt" in x:
    y=['curl -sL https://raw.githubusercontent.com/ollama/ollama/refs/heads/main/scripts/build_linux.sh | sh && ollama run llama3  "'+x["prompt"]+'"']
  else:
    y=[]
    for k in x:
      y.append(x[k])
  c="\n".join(y)
  print(c)
  r=os.popen(c)
  time.sleep(10)
  new=r.read()
  print(new)
  response = anvil.server.HttpResponse(200, new)
  response.headers['ContentType']="text/plain"
  return response
def ai(x):
  from ollama import chat
  from ollama import ChatResponse

  response: ChatResponse = chat(
    model='llama3',
    messages=[
      {
        'role': 'user',
        'content': x
      },
    ],
  )
  return response['message']['content']
@anvil.server.route("/ask/:x")
def ask(x):
  return str(ai(x))
ai("hi")