from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import html
import openai

hostName = 'localhost'
serverPort = 8080


f = open('Options.json','r')
options = json.load(f)
f.close()


# OpenAI model
if(options['model'] == 'text-embedding-ada-002'):
    f = open('secrets.json','r')
    secrets = json.load(f)
    f.close()
    openai.organization = secrets['organization']
    openai.api_key = secrets['api_key']
else:
    model = SentenceTransformer(options['model'])

opts = [option['url'] if option['type'] == 'url' else option['result'] for option in options['options']]
opt_enc = [option['encoding'] for option in options['options']]

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        prompt = ''
        if(self.path[0:4] == '/?q='):
            prompt = self.path[4:].replace('+', ' ')
            parts = prompt.split('%')
            tmp = parts[0]
            for part in parts[1:]:
                tmp += chr(int(part[:2], 16)) + part[2:]
            prompt = tmp
            print(prompt)

        if(prompt != ''): # prompt is supplied, show result
            encoding = None
            if(options['model'] == 'text-embedding-ada-002'):
                encoding = openai.Embedding.create(input = [prompt], model='text-embedding-ada-002')['data'][0]['embedding']
            else:
                encoding = model.encode(prompt)
            
            sim = cosine_similarity([encoding], opt_enc)
            answer = opts[sim[0].tolist().index(max(sim[0]))]
            print('Similarity: %f, %s' % (max(sim[0]), answer))
            self.wfile.write(bytes('<html><head>', 'utf-8'))
            self.wfile.write(bytes('<title>Sample AI</title><style>body {font-size: 2em;}</style>', 'utf-8'))
            if(answer[:5] == 'https'):
                self.wfile.write(bytes('<meta http-equiv="Refresh" content="0; url=\''+answer+'\'" />', 'utf-8'))
                self.wfile.write(bytes('</head><body>Redirecting to dashboard. Click <a href="'+answer+'">here</a> if not redirected.</body></html>', 'utf-8'))
            else: # answer like SELECT
                self.wfile.write(bytes('</head><body><p>Jim: '+prompt+'</p><p>AI: '+answer+'</p></body></html>', 'utf-8'))
        else: # prompt == '', show prompt page
            self.wfile.write(bytes('<html><head><title>Sample AI</title><style>body {font-size: 2em;} input {font-size: 1em;}</style></head>', 'utf-8'))
            self.wfile.write(bytes('<body>', 'utf-8'))
            #self.wfile.write(bytes('<a target="_blank" href="https://ip.armeta.com/demo/analytics/sales-opportunity?query=eyJmYW1pbHkiOjd9">Result</a>', 'utf-8'))
            self.wfile.write(bytes('<form target="_blank" method="get" autocomplete="off">', 'utf-8'))
            self.wfile.write(bytes('<label for="q">What would you like to see?</label><br>', 'utf-8'))
            self.wfile.write(bytes('<input type="text" size="80" name="q" required autocomplete="false"><br>', 'utf-8'))
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