import facebook
import json
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response
from django.http import HttpResponse
from django.contrib.auth import logout
from django.conf import settings
from social_auth.models import UserSocialAuth
from collections import Counter
import urllib
import urllib2

@login_required(redirect_field_name="login/facebook")
def FacebookFriends(request):
    myUser = request.user 
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser) 
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    print(token)
    if(token):
      graph = facebook.GraphAPI(token)
      user_profile = graph.get_object("me")
      name = user_profile["name"]
      friends = graph.get_connections("me", "friends")["data"]
      return HttpResponse(json.dumps(friends), mimetype="application/json")
    else:
      args=["Mike", "Dillon", "Alejandro", "Victoria"]
      return HttpResponse(json.dumps(args), mimetype="application/json")

@login_required(redirect_field_name="login/facebook")
def FacebookFriendsCheckins(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
        PLACE_TYPE = "RESTAURANT/CAFE"
	queries = {"q1":"select author_uid, coords, target_id, message, timestamp from checkin WHERE author_uid in(SELECT uid2 FROM friend WHERE uid1 = me() limit 200) ORDER BY timestamp",
"q2":"select page_id, type, description, talking_about_count, were_here_count from page where type='RESTAURANT/CAFE' and page_id in (select target_id from #q1)",
"q3":"select uid, first_name, last_name from user where uid in (select author_uid from #q1)"}
        data = graph.fql(queries)
	return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required(redirect_field_name="login/facebook")
def FacebookStatusByLikes(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
        query = "select object_id from comment where object_id in (select status_id from status WHERE uid in(SELECT uid2 FROM friend WHERE uid1 = me() limit 200))"
        query2 = "select status_id, message from status where uid in (SELECT uid2 FROM friend WHERE uid1 = me() limit 200)"
        data = graph.fql(query)
        posts = graph.fql(query2)
        countLikes = Counter()
        for obj in data:
           countLikes.update({obj["object_id"]: 1})
        most_common = countLikes.most_common(50)
        common_list = Counter()
        url = 'http://text-processing.com/api/sentiment/'
        for obj in posts:
           for common in most_common:
              if(obj["status_id"] == common[0]):
                 values = {'text':obj["message"].encode('utf-8')}
                 data = urllib.urlencode(values)
                 response = urllib2.urlopen(url, data)
                 content = response.read()
                 data = json.loads(content)
                 prob = data["probability"]
                 score = 1.3*prob["neg"] + prob["pos"]
                 common_list.update({obj["message"]:score})
        return HttpResponse(json.dumps(common_list), mimetype="application/json")

@login_required(redirect_field_name="login/facebook")
def FacebookFriendStatus(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
        query = "select description, actor_id from stream where source_id in (SELECT uid2 FROM friend WHERE uid1 = me() limit 200);"
        data = graph.fql(query)
        return HttpResponse(json.dumps(data), mimetype="application/json")



def FacebookUsersGroups(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
	user_groups = graph.get_connections("me", "groups")["data"]
        return HttpResponse(json.dumps(user_groups), mimetype="application/json")

def FacebookUserLikes(request): 
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
        user_likes = graph.get_connections("me", "likes")["data"]
        return HttpResponse(json.dumps(user_likes), mimetype="application/json")

def ParseLocations(possibleLocations, locations):
    result = []
    for location in locations:
	if(location["name"] in possibleLocations["name"]):
	    result.append(location)
    return result



