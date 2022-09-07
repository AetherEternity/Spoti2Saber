#/usr/bin/env python3
import requests
import os
import json
import string
import argparse

def levenstein(str_1, str_2):
    n, m = len(str_1), len(str_2)
    if n > m:
        str_1, str_2 = str_2, str_1
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if str_1[j - 1] != str_2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

def getspotisongs(oauth_token):
    print("\nFetching user library\n")
    r=requests.get("https://api.spotify.com/v1/me/tracks?limit=50",headers={"Authorization": "Bearer "+oauth_token})
    resp=r.json()
    songs=[]
    while True:
        for song in resp['items']:
            songs.append({"artist":song['track']['artists'][0]['name'],"track":song['track']['name']})
        print(resp['next'])
        if not resp['next']:
            break
        r=requests.get(resp['next'],headers={"Authorization": "Bearer "+oauth_token})
        resp=r.json()
    return songs

def findurls(songs):
    urls={}
    for song in songs:
        r=requests.get('https://api.beatsaver.com/search/text/0?sortOrder=Relevance',params={"q":song["artist"]+" "+song["track"]})
        try:
            resp=r.json()
        except:
            continue
        print ("\n"+song["artist"]+" - "+song["track"])
        songname=song["artist"]+" - "+song["track"]
        songname_rev=song["track"]+" - "+song["artist"]
        cnt=0
        if 'docs' in resp:
            cnt+=1
            urls[songname]=[]
            for map in resp['docs']:
                lev=levenstein(map["name"],songname)
                proportion=100-int((lev/(len(map["name"])+len(songname)))*100)
                lev_rev=levenstein(map["name"],songname_rev)
                proportion_rev=100-int((lev_rev/(len(map["name"])+len(songname)))*100)
                ups=map["stats"]["upvotes"]
                downs=map["stats"]["downvotes"]
                url=map['versions'][0]['downloadURL']
                try:
                    updown=int((ups/(ups+downs))*100)
                except ZeroDivisionError:
                    updown=0
                if (lev_rev<lev):
                    lev=lev_rev
                    proportion=proportion_rev
                print(f'{map["name"]} LEV:{lev}({proportion}) UPDOWN:{updown}% ({ups+downs})')
                urls[songname].append({"cnt":cnt,"lev":lev,"proportion":proportion,"updown":updown,"ups":ups,"downs":downs,"url":url,"mapname":map["name"]})
    return urls
                

def processurls(urls,who,limit):
    playlist={"playlistTitle":"Spotify "+who,"playlistAuthor":"me","playlistDescription":"","_filename":"Spotify_"+who+".bplist","songs":[]}

    for songname in urls:
        cnt=0
        print("\nSearching for "+songname+":")
        for map in urls[songname]:
            if map["lev"]==0 and map["updown"]>60:
                print(map["mapname"])
                playlist["songs"].append({"hash":map["url"].split("/")[-1][:-4],"songName":map["mapname"]})
                continue
            if map["proportion"]>66 and map["updown"]>60:
                print(map["mapname"])
                cnt+=1
                playlist["songs"].append({"hash":map["url"].split("/")[-1][:-4],"songName":map["mapname"]})
                if cnt==limit:
                    break
    return playlist

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('playlist_name', help='Playlist name')
    parser.add_argument('oauth_token', help='Spotify OAUTH token')
    parser.add_argument('--limit', type=int, default=3, help='Max number of "similar" songs (Default: 3). May flood your playlist with unrelated songs if set too high')
    args = parser.parse_args()
    who=args.playlist_name
    oauth_token=args.oauth_token
    limit=args.limit
    songs=getspotisongs(oauth_token)
    urls=findurls(songs)
    playlist=processurls(urls,who,limit)
    songs=playlist["songs"]
    songsu=[dict(s) for s in set(frozenset(d.items()) for d in songs)]
    playlist["songs"]=list(songsu)

    with open("Spotify_"+who+".bplist","w") as f:
        json.dump(playlist,f) 