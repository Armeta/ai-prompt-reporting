import base64

images = ['armeta-icon.png', 'usericon.png']

for image in images:
    f = open(image, 'rb')
    data = f.read()
    f.close()
    encoded = base64.b64encode(data)
    #print(image + ' ' + str(encoded))
    out = open(image.replace('.png', '_Base64Source.txt'), 'w')
    out.write('data:image/png;base64,' + str(encoded)[2:-1])
    out.close()
