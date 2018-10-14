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

def displayline(tabs, s):
    if 0 < len(s):
        print(' '*4*tabs + s)

class TagStruct:
    """Struct to hold Tag data"""
    def __init__(self, tag, attributedict=dict(), Parent=None):
        """Tag is required, all other inputs are optional"""
        self.Tag = tag
        self.attributes = attributedict
        self.children = []
        self.parent = Parent
    def Display(self, layer=0):
        atrbstr = ""
        for a in self.attributes:
            atrbstr += " " + a + "=\"" + self.attributes[a] + "\""
        displayline(layer, "<"+self.Tag + atrbstr[:-1]+">")
        for c in self.children:
            c.Display(layer+1)
        displayline(layer, "</"+self.Tag+">")

class TagContent:
    """Struct to hold Tag content, with an identical Display function"""
    def __init__(self, word=""):
        self.word = word
    def Display(self, layer=0):
        if self.word != "":
            displayline(layer, self.word)

def xmlformatter(xmlfile):
    header = "b\'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\\r\\n"#both files start with this same header
    xmlfile = str(xmlfile)[len(header):] #strip header
    #subdivide string into encapsulating tags
    #find a tag, push prefix onto stack.
    #if a tag is a closing tag, pop the last tag.
    #if a tag is its own closing tag, treat it as a string.
    #else, push the tag onto the stack.

    string = xmlfile
    stack = []
    t2 = -1
    Root = TagStruct("Root")
    Current = Root
    while 0 != len(string):
        string = string[t2+1:] #allows the "Continue" operator to work

        #find a tag
        t0 = string.find('<')
        t1 = string[t0+1].find('<')
        t2 = string.find('>')
        
        if t0 == -1: #if there are no more tags, stop loop
            break

        if t1 != -1:
            if t1 < t2:
                continue # < sign, not a tag

        #valid tag
        if 0 < len(string[0:t0]):
            Current.children.append(TagContent(string[0:t0]))
        #displayline(len(stack), string[0:t0]) #before the tag
        #displayline(len(stack), string[t0:t2+1]) #the tag
        
        tagstr = string[t0+1:t2] #strip bracket
        
        closing = tagstr[0] == '/' #closing tag
        if closing:
            stack.pop()
            Current = Current.parent
            continue

        selfclose = tagstr[-1] == '/'
        if selfclose: #self closing tag, does not pop
            tagstr = tagstr[:-1]

        if not closing:
            tag = tagstr.split()
            data = dict()
            #print(' '*4*len(stack)+tag[0],end=": ")
            for s in tag[1:]:
                kv = s.split('=')
                data[kv[0]] = kv[1].strip('\"')
                #print(kv[0], data[kv[0]], end=",")
            #print()
            NewTag = TagStruct(tag[0],data,Current)
            Current.children.append(NewTag)
            if not selfclose:
                stack.append(tag[0])
                Current = NewTag
    #Strip root node
    if len(Root.children) == 1:
        Root = Root.children[0]
    else:
        print("Root children count:", len(Root.children))
    Root.Display()
    return Root

def ParseVariableFile(Root):
    """Parses variable xml file, returns a list. Inputs a TagStruct."""
    if Root.Tag != "sst":
        return False, None
    varlist = []
    for x in Root.children: #strip content tags
        if type(x).__name__ != "TagStruct":
            continue
        varlist.append(x.children[0].children[0].word) #skip si and t tags to get to the juicy center
    return True, varlist
    
def ParseSpreadsheet(varlist, Root):
    """Parses spreadsheet data into a simple table. Inputs variable list, and Tagstruct."""
    if Root.Tag != "worksheet":
        return False, None
    #Worksheet data is unique, convert list into dict
    attributes = dict()
    for x in Root.children: #strip content tags
        if type(x).__name__ != "TagStruct":
            continue
        attributes[x.Tag] = x

    #dimension, sheetViews, sheetFormatPr, cols, sheetData, pageMargins are available
    #only dimension and sheetdata are useful for this bot, the rest are for formatting
    #get dimensions
    dim = [0,0]
    for n in attributes["dimension"].attributes["ref"].split(":"):
        col = 0
        for x in n:
            if not x.isalpha():
                break
            col += 1
        dim[0] = ord(n[:col]) - ord('A') + 1 # row
        dim[1] = int(n[col:])                # col

    spreadsheet = [["" for x in range(dim[0])] for y in range(dim[1])] # extent of spreadsheet data
    print(dim)
    for r in attributes["sheetData"].children: # rows
        row = int(r.attributes["r"])-1
        for c in r.children:
            col = ord(c.attributes["r"][:-len(str(row))]) - ord("A")
            print(row, col)
            w = int(c.children[0].children[0].word)
            print(w)
            w = varlist[w]
            print(w)
            spreadsheet[row][col] = w
            #spreadsheet[row][col] = varlist[int(c.children[0].children[0].word)]

    print(spreadsheet)

    return True, spreadsheet
    

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
    success, varlist = ParseVariableFile(xmlformatter(z.open("xl/sharedStrings.xml").read()))
    if not success:
        return
    success, spreadsheet = ParseSpreadsheet(varlist, xmlformatter(z.open("xl/worksheets/sheet1.xml").read()))
    if not success:
        return
    
if __name__ == '__main__':
    main()
