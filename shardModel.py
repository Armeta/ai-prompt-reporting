modelFilename = './LocalModel/pytorch_model.bin'
modelFile = open(modelFilename, 'rb')

bufferSize = 90 * (2**20) # 90 MB

i = 1
chunk = modelFile.read(bufferSize)
while chunk:
    shardFile = open('./LocalModel/shards/%02d_shard_pytorch_model.bin' % (i), 'wb')
    shardFile.write(chunk)
    #print('%02d_shard_pytorch_model.bin' % (i))
    chunk = modelFile.read(bufferSize)
    i += 1