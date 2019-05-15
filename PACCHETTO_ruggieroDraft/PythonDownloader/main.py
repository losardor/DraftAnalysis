from __future__ import print_function
import httplib2
import os, io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
import auth
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.getCredentials()

http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)

def listFiles(size):
    results = drive_service.files().list(
        pageSize=size,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id'])) 

#listFiles(10)

def uploadFile(filename, filepath, mimetype):
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))

def downloadFile(file_id,filepath):
    request = drive_service.files().export_media(fileId=file_id, mimeType='text/plain')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath,'wb') as f:
        fh.seek(0)
        f.write(fh.read())


def createFolder(name):
    file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    print ('Folder ID: %s' % file.get('id'))

def searchFile(size,query):
    results = drive_service.files().list(
    pageSize=size,fields="nextPageToken, files(id, name, kind, mimeType)",q=query).execute()
    items = results.get('files', [])
    fileIds = list()
    filenames = list()
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
            fileIds.append(item['id'])
            filenames.append(item['name'])
    return fileIds, filenames

from apiclient import errors
# ...

def print_revision(service, file_id, revision_id):
  """Print information about the specified revision.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to print revision for.
    revision_id: ID of the revision to print.
  """
  try:
    revision = service.revisions().get(
        fileId=file_id, revisionId=revision_id, alt='media').execute()
    #print(revision.items())
    print('Revision ID: %s' % revision['id'])
    print('Modified Date: %s' % revision['modifiedTime'])
    if revision.get('pinned'):
      print('This revision is pinned')
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

from apiclient import errors
# ...

def retrieve_revisions(service, file_id):
  """Retrieve a list of revisions.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve revisions for.
  Returns:
    List of revisions.
  """
  try:
    revisions = service.revisions().list(fileId=file_id).execute()
    revisionIds = [rev['id']  for rev in revisions['revisions']]
    return revisionIds
  except errors.HttpError, error:
    print('An error occurred: %s' % error)
  return None

#uploadFile('Migo.jpg', 'Migo.jpg', 'image/jpeg')
query = "('16mIeA42QEC4QTXxNhQBwoAWMRe7UHIbB' in parents) and (mimeType contains 'application/vnd.google-apps.document')"
fileIds, filenames = searchFile(1000,query)
for fileid,  filename in zip(fileIds, filenames):
    downloadFile(fileid, filename)
#items = retrieve_revisions(drive_service, '1PYnidPjQaKVEZz8ZJNBJ-qBZluLdDdyvtiSseMd3bSQ')
#print_revision(drive_service, '1PYnidPjQaKVEZz8ZJNBJ-qBZluLdDdyvtiSseMd3bSQ',items[0])
#print(items)

#print_revision(drive_service, '1jQSqMGFemKuvOiZKY_vRroWSJ8IQl-e7D-_0ye2lUf4',  589)