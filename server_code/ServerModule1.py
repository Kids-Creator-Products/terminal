import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.files
from anvil.files import data_files
import anvil.server
import os,time
import io
import numpy as np
import onnxruntime as ort
from PIL import Image
from transformers import TrOCRProcessor
import anvil.media
"""os.system("curl -fsSL https://ollama.com/install.sh | sh")
os.system("mkdir -p $HOME/.local/bin && curl -L https://ollama.com/download/ollama-linux-amd64.tar.zst | tar --strip-components=1 -xf - -C $HOME/.local/bin bin/ollama")
os.system("export PATH=$HOME/.local/bin:$PATH")
os.system("source ~/.bashrc || source ~/.profile")
os.system("ollama serve")"""
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
  y=[]
  for k in x:
    y.append(x[k])
  c="\n".join(y)
  print(c)
  r=os.popen(c)
  time.sleep(12)
  new=r.read()
  print(new)
  response = anvil.server.HttpResponse(200, new)
  response.headers['ContentType']="text/plain"
  return response


# 1. Initialize the processor and ONNX sessions once globally
# Note: TrOCRProcessor handles tokenizing and image feature extraction
PROCESSOR = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")

# 2. Fetch the files directly from Anvil's local Data Files
ENCODER_PATH = data_files['encoder_model.onnx']
DECODER_PATH = data_files['decoder_model.onnx']

ENCODER_SESS = ort.InferenceSession(ENCODER_PATH, providers=['CPUExecutionProvider'])
DECODER_SESS = ort.InferenceSession(DECODER_PATH, providers=['CPUExecutionProvider'])

@anvil.server.callable
def perform_ocr(image_media):
  """
    Accepts an uploaded Anvil Media object (image), processes it,
    and runs TrOCR natively via onnxruntime without Uplink.
    """
  # Convert Anvil Media bytes to PIL Image
  img_bytes = image_media.get_bytes()
  image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

  # Preprocess image into required pixel values
  inputs = PROCESSOR(images=image, return_tensors="np")
  pixel_values = inputs.pixel_values.astype(np.float32)

  # --- Step 1: Run Encoder ---
  encoder_inputs = {ENCODER_SESS.get_inputs()[0].name: pixel_values}
  encoder_outputs = ENCODER_SESS.run(None, encoder_inputs)[0]

  # --- Step 2: Autoregressive Decoding Loop ---
  # Start generation with the decoder's Bos (Beginning of sentence) token
  bos_token_id = PROCESSOR.tokenizer.bos_token_id
  eos_token_id = PROCESSOR.tokenizer.eos_token_id

  generated_tokens = [bos_token_id]
  max_length = 64

  for _ in range(max_length):
    # Shape: (batch_size, sequence_length)
    input_ids = np.array([generated_tokens], dtype=np.int64)

    decoder_inputs = {
      DECODER_SESS.get_inputs()[0].name: input_ids,
      DECODER_SESS.get_inputs()[1].name: encoder_outputs
    }

    # Get next-token logits from decoder
    decoder_outputs = DECODER_SESS.run(None, decoder_inputs)[0]
    next_token_logits = decoder_outputs[:, -1, :]
    next_token = int(np.argmax(next_token_logits, axis=-1)[0])

    generated_tokens.append(next_token)

    # Break early if end-of-sentence token is hit
    if next_token == eos_token_id:
      break

    # Decode the accumulated token IDs back into readable text
  text = PROCESSOR.decode(generated_tokens, skip_special_tokens=True)
  return text.strip()
