from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.js
import anvil.http

class Form1(Form1Template):
  def __init__(self, **properties):
    super().__init__(**properties)
    x=anvil.http.request("https://cool-guys-bfc2.github.io/Super-AutoTerminal/term.sh")
    self.text_area_1.text=x.get_bytes().decode("utf-8")
  @handle("button_1", "click")
  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    x=self.text_area_1.text
    def args(x):
      y="/term?0=echo%20Running"
      ind=1
      for i in x.split("\n"):
        y=y+"&"+str(ind)+"="+str(i)
        ind+=1
      return y
    anvil.js.window.open(anvil.server.get_app_origin().strip("/")+args(x),"about:blank")
    
