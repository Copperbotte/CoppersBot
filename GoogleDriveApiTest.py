#this was modified from these stack overflow samples.
#https://stackoverflow.com/questions/38421060/how-to-use-google-drive-api-for-python
#https://stackoverflow.com/questions/36173356/google-drive-api-download-files-python-no-files-downloaded
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import io
import zipfile
from apiclient.http import MediaIoBaseDownload


# If modifying these scopes, delete the file token.json.
#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive'

#def main():
if True:
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('({1}) {0}'.format(item['name'], item['id']))

    fileid = "1pcW5wkpwrhhAH2brE6yofQcjilgF7seZ"
    results = service.files().get_media(fileId=fileid)
    fh = io.BytesIO()#io.FileIO("download.xlsx", "wb")
    downloader = MediaIoBaseDownload(fh, results)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    z = zipfile.ZipFile(fh)
    for n in z.namelist():
        print(n)
    #f.write(fh.read())
    #f.close()
    
#if __name__ == '__main__':
#    main()
