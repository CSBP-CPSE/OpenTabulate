import urllib.request

def fetch_url(URL, filename):
    try:
        response = urllib.request.urlopen(URL)
        data = response.read()
    except:
        print("[W] fetch_url failed, attempting fallback 'file'.")
        return
    # if the exception was not caught, proceed to write
    fw = open('raw/' + filename, 'wb')
    fw.write(data)
    fw.close()
