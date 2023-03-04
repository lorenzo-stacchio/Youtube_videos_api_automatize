#!/usr/bin/python
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib import get_user_credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.oauth2 as gauth2
from datetime import datetime
import json, time, tqdm 

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

## AUTHORIZED FLOW 
# WRITE THE API KEY in a unique row in the secret_key.txt file
DEVELOPER_KEY = open("secret_key.txt").readlines()[0]




def get_all_ids_in_playlist(youtube_api, playlist_id):
  ids = []
  nextPageToken = "something"
  i = 0
  while (nextPageToken):
    search_response = youtube_api.playlistItems().list(
      playlistId = playlist_id,
      part='id,snippet',
      maxResults = 10,
      pageToken = None if i==0 else nextPageToken
      ).execute()
    
    i+=1
    if "nextPageToken" in search_response.keys():
      nextPageToken = search_response["nextPageToken"]
    else:
      nextPageToken = None
     
    for search_result in search_response.get('items', []):
        ids.append(search_result['snippet']['resourceId']["videoId"])
  
  return list(set(ids)) # just to be sure 

def youtube_search(youtube_api,list_id_in_playlist,options):

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube_api.search().list(
    q=options.q,
    part='id,snippet',
    order = "date",
    maxResults=options.max_results
  ).execute()

  videos = []
  new_ids = []
  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append({"id":search_result['id']['videoId'], "title": search_result['snippet']['title']})
      new_ids.append(search_result['id']['videoId'])
  print(len(new_ids))

  # FILTER NEW IDS 
  new_ids = list(set(new_ids).difference(set(list_id_in_playlist)))
  # print(len(new_ids))
  # print(new_ids)
  return sorted(new_ids)

def like_comment_add_video_ids(youtube_api,list_ids, comment_template, playlistId_to_add_template, index_start):
  report_links = []
  for ids in tqdm.tqdm(list_ids):
    time.sleep(10)
    video_url = "https://www.youtube.com/watch?v=%s" %ids
    print("video link %s" % video_url)
    
    try:
      # comment
      # https://developers.google.com/youtube/v3/docs/commentThreads/insert
      youtube_api.commentThreads().insert(
          part="snippet",
          body={
            "snippet": {
              "videoId": ids,
              "topLevelComment": {
                "snippet": {
                  "textOriginal": comment_template
                }
              }
            }
          }
          ).execute()
      time.sleep(5)
      # like
      youtube_api.videos().rate(
          id = ids,
          rating='like'
          ).execute()
      time.sleep(5)    
      # add to playlist
      youtube_api.playlistItems().insert(
        part="snippet",
          body={
            "snippet": {
              "playlistId": playlistId_to_add_template,
              "position": index_start,
              "resourceId": {
                "kind": "youtube#video",
                "videoId": ids
              }
            }
          }
      ).execute()
      time.sleep(5)
      report_links.append(video_url)
      index_start +=1
    except HttpError as e:
      print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
      if "The request cannot be completed because you have exceeded your" in e.reason:
        exit()
      continue
    
  return report_links

  

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--q', help='Search term', default='digimon amv|digimon asmv')
  parser.add_argument('--max-results', help='Max results', default=20)
  args = parser.parse_args()
  
  token_secrets = json.load(open("token.json"))
  
  credentials = gauth2.credentials.Credentials(
      token_secrets["token"],
      refresh_token=token_secrets['refresh_token'],
      token_uri=token_secrets['token_uri'],
      client_id=token_secrets['client_id'],
      client_secret=token_secrets['client_secret'],)

  
  youtube_api = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY, credentials = credentials)

  playlist_id = "".join(open("playlistId.txt", encoding='utf-8').readlines())
  
  try:
    list_id_in_playlist = get_all_ids_in_playlist(youtube_api=youtube_api, playlist_id=playlist_id)
    novel_id_to_comment_and_add = youtube_search(youtube_api,list_id_in_playlist,args)
    comment_template = "".join(open("comment_template.txt", encoding='utf-8').readlines())
    
    links_report = like_comment_add_video_ids(youtube_api=youtube_api,list_ids=novel_id_to_comment_and_add, 
                   comment_template=comment_template, playlistId_to_add_template = playlist_id, index_start = len(list_id_in_playlist))
    # plot like and commented video
    
    td_string = datetime.now().strftime("%d_%m_%Y")
    
    with open("report_%s.txt" % td_string, "w") as f:
      for l in links_report:
        f.write(l)
        
  except HttpError as e:
    print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.reason))    