from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.js

class Form1(Form1Template):
  def __init__(self, **properties):
    super().__init__(**properties)

  @handle("button_1", "click")
  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    x=self.text_area_1.text
    anvil.js.window.open(anvil.server.get_app_origin().strip("/")+"/term?1="+x,"about:blank")
    
