from http.server import BaseHTTPRequestHandler, HTTPServer

class RemoteInterface():
  videolooper = None

  def __init__(self):
    self.server = HTTPServer(('', 80), RemoteInterfaceServer)
    self.server.serve_forever()

class RemoteInterfaceServer(BaseHTTPRequestHandler):
    def _set_headers(self):
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

    def mainMenu(self, msg=""):
      status = ""
      if RemoteInterface.videolooper.get_playback_status():
        status = "Playing"
      else:
        status = "Paused"
      html =  f"""
      <!DOCTYPE html>
      <html>
        <head>
          <title>Video Wall Controller</title>
          <style>
            body {{
              font-family: Arial, Helvetica, sans-serif;
            }}
          </style>
        </head>
        <body>
          <h1>Raspberry Pi Video Wall Source</h1>
          <h2>Control Panel</h2>
          <p><strong>Current Status:</strong> {status}</p>
          <p>{msg}</p>
          <form method="POST">
            <button type="submit" name="skip_vid" value="true">Skip Current Video</button><br><br>
            <button type="submit" name="pauseplay_vid" value="true">Resume/Pause Playback</button>
          </form>
        </body>
      </html>
      """
      return html.encode("utf8")

    def do_GET(self):
      self._set_headers()
      self.wfile.write(self.mainMenu())

    def do_POST(self):
      content_length = int(self.headers['Content-Length'])
      self._set_headers()
      try:
        msg = ""
        post_data_bytes = self.rfile.read(content_length)
        post_data_str = post_data_bytes.decode("UTF-8")
        list_of_post_data = post_data_str.split('&')
        post_data_dict = {}
        for item in list_of_post_data:
            variable, value = item.split('=')
            post_data_dict[variable] = value

        if 'skip_vid' in post_data_dict:
          if post_data_dict['skip_vid'] == "true":
            RemoteInterface.videolooper.skip_video()
            msg = msg + "Skipping current video...<br>"

        if 'pauseplay_vid' in post_data_dict:
          if post_data_dict['pauseplay_vid'] == "true":
            RemoteInterface.videolooper.pauseplay_video()
            msg = msg + "Resuming/pausing playback...<br>"

        self.wfile.write(self.mainMenu(msg))
      except Exception as e:
        print(e)
        self.wfile.write(self.mainMenu("An error has occured processing your request."))
