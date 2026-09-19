import anvil.server
import os,time
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
def term(x):
  y=[]
  for k in x:
    y.append(x[k])
  c=y.join("\n")
  r=os.popen(c)
  while r.read()=="":
    pass
  x=False
  new=r.read()
  old=""
  i=0
  while not (x or i>5):
    i+=1
    old=new
    new=r.read()
    x=(old==new)
    time.sleep(3)
  print(r.read())
  o=r.read()
  return o