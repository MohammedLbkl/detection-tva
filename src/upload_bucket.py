from google.cloud import storage

# Initialiser le client
client = storage.Client(project='project-3b645245-14b9-4448-94f')

buckets = list(client.list_buckets())
print(buckets)

buckets = client.get_bucket('bucket_detection-tva')

print(buckets)

blobs = buckets.list_blobs()
for blob in blobs:
    print(blob.name)
    blob.delete()

exit()
blob = buckets.blob('test2.txt')

blob.upload_from_filename('output/doc1.md')



blobs = buckets.list_blobs()
for blob in blobs:
    print(blob.name)