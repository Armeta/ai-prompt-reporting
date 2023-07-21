from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

hostName = 'localhost'
serverPort = 8080


f = open('Options.json','r')
options = json.load(f)
f.close()

model = SentenceTransformer(options['model'])

opt_url = [option['url'] for option in options['options']]
opt_enc = [option['encoding'] for option in options['options']]

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        prompt = ''
        if(self.path[0:4] == '/?q='):
            prompt = self.path[4:]

        if(prompt != ''):
            encoding = model.encode(prompt)
            sim = cosine_similarity([encoding], opt_enc)
            url = opt_url[sim[0].tolist().index(max(sim[0]))]
            print('Similarity: %f, %s' % (max(sim[0]), url))
            self.wfile.write(bytes('<html><head>', 'utf-8'))
            self.wfile.write(bytes('<title>Sample AI</title>', 'utf-8'))
            self.wfile.write(bytes('<meta http-equiv="Refresh" content="0; url=\''+url+'\'" />', 'utf-8'))
            self.wfile.write(bytes('</head><body>Redirecting to dashboard. Click <a href="'+url+'">here</a> if not redirected.</body></html>', 'utf-8'))
        else:
            self.wfile.write(bytes('<html><head><title>Sample AI</title><style>body {font-size: 2em;} input {font-size: 1em;}</style></head>', 'utf-8'))
            self.wfile.write(bytes('<body>', 'utf-8'))
            #self.wfile.write(bytes('<a target="_blank" href="https://ip.armeta.com/demo/analytics/sales-opportunity?query=eyJmYW1pbHkiOjd9">Result</a>', 'utf-8'))
            self.wfile.write(bytes('<form target="_blank" method="get">', 'utf-8'))
            self.wfile.write(bytes('<label for="q">What would you like to see?</label><br>', 'utf-8'))
            self.wfile.write(bytes('<input type="text" size="80" name="q" required><br>', 'utf-8'))
            self.wfile.write(bytes('<input type="submit">', 'utf-8'))
            self.wfile.write(bytes('</form>', 'utf-8'))
            self.wfile.write(bytes('</body></html>', 'utf-8'))

if __name__ == '__main__':        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print('Server started http://%s:%s' % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Server stopped.')