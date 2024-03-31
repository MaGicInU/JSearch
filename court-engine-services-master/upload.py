import requests
import os


def uploadAllfilesToIndex():
    all_files = []
    for dirpath, dirnames, filenames in os.walk("D:\\Downloads\\Judgements"):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            all_files.append(os.path.join(dirpath, filename))
    print(all_files)
    for filePath in all_files:
        print("Starting upload")
        try:
            with open(filePath, 'rb') as f:
                r = requests.post(
                    'http://127.0.0.1:8000/pdfUpload', files={'file': f})
                print("upload completed")
        except Exception as e:
            print("skipping {0}".format(filePath), end="\n\n")
            print(e)


uploadAllfilesToIndex()
