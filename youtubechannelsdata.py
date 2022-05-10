from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

api_key = 'AIzaSyD7ns2KREJQNywrl5VjqDla5cNT64n2YB8'
channel_ids = ['UC-lHJZR3Gqxm24_Vd_AJ5Yw', #PewDiePie
               'UCYiGq8XF7YQD00x7wAd62Zg', #JuegaGerman
               'UCV4xOVpbcV8SdueDCOxLXtQ', #Fernanfloo
               'UCXazgXDIYyWH-yXLAkcrFxw', #ElrubiusOMG
               'UCam8T03EOFBsNdR0thrFHdQ', #Vegeta777
               'UCTkXRDQl0luXxVQrRQvWS6w'  #Dream
              ]
               

youtube = build('youtube','v3',developerKey=api_key)

## Function to get channel statistics
def get_channel_stats(youtube,channel_ids):
    all_data = []
    request = youtube.channels().list(
                part= 'snippet,contentDetails,statistics',
                id = ','.join(channel_ids))
    response = request.execute()
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'], 
                    Subscribers = response['items'][i]['statistics']['subscriberCount'], 
                    Views = response['items'][i]['statistics']['viewCount'], 
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])

        all_data.append(data)
    
    return all_data
        
channel_statistics = get_channel_stats(youtube,channel_ids)
channel_data = pd.DataFrame(channel_statistics)

## Top Gaming Channels on YouTube
channel_data
channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data.dtypes

sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='Channel_name', y='Subscribers', data=channel_data) 
ax = sns.barplot(x='Channel_name', y='Views', data=channel_data) 
ax = sns.barplot(x='Channel_name', y='Total_videos', data=channel_data) 

## Function to get video ids
channel_data
playlist_id = channel_data.loc[channel_data['Channel_name']=='Dream', 'playlist_id'].iloc[0]
def get_video_ids(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()
    
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
        
    return video_ids
video_ids = get_video_ids(youtube, playlist_id)

## List of Video ID Tags for YouTuber "Dream"
video_ids

## Function to get video details for Youtuber "Dream"
def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()
        
        for video in response['items']:
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Views = video['statistics']['viewCount'],
                               Likes = video['statistics']['likeCount'],
                               #Youtube Removing Dislike Count: https://www.youtube.com/watch?v=kxOuG8jMIgI&ab_channel=YouTubeCreators
                               Comments = video['statistics']['commentCount']
                               )
            all_video_stats.append(video_stats)
    
    return all_video_stats
  
video_details = get_video_details(youtube, video_ids)

video_data = pd.DataFrame(video_details)
video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data

top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)
top10_videos

## Dream's Top 10 Videos
ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)

## Top 10 Videos Statistical Data
video_data
video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
video_data

videos_per_month = video_data.groupby('Month', as_index=False).size()

## Number of Dream's Videos Monthly Uploads
videos_per_month
sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories=sort_order, ordered=True)
videos_per_month = videos_per_month.sort_index()

## Dream's Monthly Video Uploads
ax2 = sns.barplot(x='Month', y='size', data=videos_per_month)

## Get each video details
video_df = get_video_details(youtube, video_ids)
video_df

video_data.to_csv('Video_Details(Dream).csv')
