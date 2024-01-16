from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import json
import logging
#import pandas as pd
import PyPDF2
import re
#import sys
import threading
import time
import unicodedata
from urllib.parse import urlparse

# http://127.0.0.1:8080/ 
server_name = "localhost"
server_port = 8080
glob_text_map = {} # TODO: Wann löschen?
counter = 0
lock_counter = threading.Lock()

# Wie Infos übergene?
# - Javascript -> Python
# - Python -> Javascript
# pdf und query herunterladen
# txt zurück senden

# TODO: Was is mit PDF Datein, welche Bilder beinhalten?

# TODO: Den gefilterten Text speichern? (Für weiter Suche)
# - gute Idee mit großen Datein?
# - wie gut mit mehreren Detein?

############################## Helper Functions ###############################
def eliminateCharacters(text):
  # Eliminate formatting characters from the extracted text
  # retval = "".join(chr(ch) for ch in text if unicodedata.category(chr(ch))[0]!="C")
  
  # Substitute sentence endings for space to handle linebreaks
  retval = re.sub('\.|\!|\?', ' ', text)
  # Eliminate special characters from the extracted text
  retval = re.sub('[^A-Za-z0-9 ]+','', retval)
  # Eliminate any remaining multible spaces
  retval = re.sub(' +', ' ', retval)
  
  return retval

############################### Main Functions ################################
##
# document ... byte object of pdf
##
def extractText(document):
  cleaned_text = ""
  buffer_reader = io.BytesIO(document)
  pdf_reader = PyPDF2.PdfReader(buffer_reader) # open a document
  
  i = 0
  while i < len(pdf_reader.pages):
    # logging.info("Current page: %d", i)
    text = pdf_reader.pages[i].extract_text()
    cleaned_text = cleaned_text + '' + text
    i += 1

  return cleaned_text

##
# search_terms ... list with all the user specified searchterms
# text ... string with the text to be procesed
##
def stopWords(search_terms, text):

  stop_words = open("stop_words_edited.txt").read().split()
  
  # Check if user specified term is a stopword
  if search_terms:
    stop_words = list(filter(lambda l: l not in search_terms, stop_words))
  
  # Filter out unwanted words
  filtered = list(filter(lambda l: l not in stop_words, text.split()))
  
  # Convert list to a string
  filtered = ' '.join(filtered)
  # print(filtered)
  return filtered
  
################################### Server ####################################
class Server(BaseHTTPRequestHandler):
  def end_headers(self):
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET')
      self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
      return super(Server, self).end_headers()

  def _set_header(self, response_type, msg_len):
    # POST
    if(response_type == 'POST'):
      self.send_response(200)
      self.send_header('Content-type', 'json/encoding=utf-8')
      self.send_header('Content-Length', msg_len)
      self.end_headers()
    # GET
    elif(response_type == 'GET'):
      self.send_response(200)
      self.send_header('Content-type', 'text/encoding=utf-8')
      self.end_headers()
    # Unintended request
    else:
      self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write(bytes("<body>", "utf-8"))
      self.wfile.write(bytes("<p>Could not resolve request.</p>", "utf-8"))
      self.wfile.write(bytes("</body></html>", "utf-8"))

  # TODO: Check userinput for correctness
  def do_GET(self):
    logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
    
    # Extract info from header
    #content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    #get_data = self.rfile.read(content_length) # <--- Gets the data itself
    query = urlparse(self.path).query
    query_components = dict(qc.split("=") for qc in query.split("&"))
    #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",str(self.path), str(self.headers), get_data)
    #json_info = json.loads(get_data)
    UID = query_components["UID"]
    # Get proccesed text from storage
    response =  json.dumps({ "text" : stopWords([],glob_text_map[int(UID)])}) # TODO: Get user specified serach terms
    
    # Prepear header and payload
    self._set_header('GET', len(response))
    self.wfile.write(bytes(response, "utf-8"))
    
    logging.info("Get request finished\n")

  def do_OPTIONS(self):
    self.send_response(200, "ok")
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
    self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")
    self.end_headers()

  # TODO: Check userinput for correctness
  def do_POST(self):
    global counter
    logging.info("POST request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
    
    # Extract info from header
    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    post_data = self.rfile.read(content_length) # <--- Gets the data itself
    #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",str(self.path), str(self.headers), get_data)
    
    # Generate UID and timestamp
    lock_counter.acquire()
    counter += 1
    UID = int(time.time() + counter)
    lock_counter.release()
    timestamp = time.time()
    
    # Procces pdf
    procced_text = eliminateCharacters(extractText(post_data))
    
    # Map Uid to pdf name
    glob_text_map[UID] = procced_text
    name = "TO BE EXTRATEC?" # TODO: Get pdf name
    #response = "{ \"{UID}\":\"%d\", \"{name}\":\"%s\", \"{timestamp}\":\"%s\"} " % (UID, name, str(timestamp))
    response  = json.dumps({ "UID" : str(UID), "name" : name, "timestamp" : str(timestamp)})
    
    # Prepear header and payload
    self._set_header('POST', len(response))  
    self.wfile.write(bytes(response, "utf-8"))
    
    logging.info("POST request finished\n")

################################### "Main" ####################################
#print("Hello world!")

# Server GET actions
#search_terms = ["enough", "if", "us"]
#text = extractText("test_data/Simple_text.pdf")
# print(text)
#filtered = stopWords(search_terms, text)
#print(filtered)
# Write result to .txt
#out = open("output.txt", "wb") # create a text output
#out.write(bytes(filtered, "utf8")) # write text of page
#out.close()

webserver = HTTPServer((server_name, server_port), Server)
print(webserver)

logging.basicConfig(level=logging.INFO)
logging.info("Starting webserver...\n")

try:
  webserver.serve_forever()
except KeyboardInterrupt:
  pass

webserver.server_close()
logging.info("Stopping webserver...\n")