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

def displayline(stack, s):
    if 0 < len(s):
        print(' '*4*len(stack) + s)

def xmlformatter(xmlfile):
    header = "b\'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\\r\\n"#both files start with this same header
    xmlfile = str(xmlfile)[len(header):] #strip header
    #subdivide string into encapsulating tags
    #find a tag, put its prefix string into an array
    #if a tag is a closing tag, pop the last tag.
    #if a tag is its own closing tag, treat it as a string.
    #else, push the tag onto the stack.

    string = xmlfile
    stack = []
    t2 = -1
    while 0 != len(string):
        string = string[t2+1:] #allows the "Continue" operator to work

        #find a tag
        t0 = string.find('<')
        t1 = string[t0+1].find('<')
        t2 = string.find('>')
        
        if t0 == -1: #if there are no more tags, stop loop
            displayline(stack, string)
            break

        if t1 != -1:
            if t1 < t2:
                continue # < sign, not a tag

        #valid tag
        displayline(stack, string[0:t0]) #before the tag
        displayline(stack, string[t0:t2+1]) #the tag
        
        tagstr = string[t0+1:t2] #strip bracket
        
        closing = tagstr[0] == '/' #closing tag
        if closing:
            stack.pop()

        selfclose = tagstr[-1] == '/'
        if selfclose: #self closing tag, does not pop
            tagstr = tagstr[:-1]

        if not closing:
            tag = tagstr.split()
            data = dict()
            print('.'*4*len(stack)+tag[0],end=": ")
            for s in tag[1:]:
                kv = s.split('=')
                data[kv[0]] = kv[1].strip('\"')
                print(kv[0], data[kv[0]], end=",")
            print()
            if not selfclose:
                stack.append(tag[0])
    
    
def main():
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
    xmlformatter(z.open("xl/sharedStrings.xml").read())
    xmlformatter(z.open("xl/worksheets/sheet1.xml").read())
    
    
if __name__ == '__main__':
    main()
