from urllib import request
import io
import zipfile

data_url="ftp://webftp.vancouver.ca/OpenData/csv/business_licences_csv.zip"


with request.urlopen(data_url) as response:
    data = response.read()
    archive = zipfile.ZipFile(io.BytesIO(data))
    data_stream = archive.read('business_licences.csv')
    #byte_write = open('test.csv', 'w', encoding="utf-8")
    #byte_write.write(data_stream.decode("utf-8"))
    byte_write = open('test.csv', 'wb')
    byte_write.write(data_stream)
    # close io stream
    byte_write.close()
    archive.close()
