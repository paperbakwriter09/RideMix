import facebook
import json
import random
from itertools import groupby
import time
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
import base64

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
	queries = {"q1":"select author_uid, coords, target_id, message, timestamp, checkin_id from checkin WHERE author_uid in(SELECT uid2 FROM friend WHERE uid1 = me() limit 200) limit 200",
"q2":"select name, phone, page_id, description, talking_about_count, were_here_count from page where type='RESTAURANT/CAFE' and page_id in (select target_id from #q1)",
"q3":"select uid, first_name, last_name from user where uid in (select author_uid from #q1)"}
        graph_data = graph.fql(queries)
        query_set1 = graph_data[0]["fql_result_set"]
        rankings = Counter()
        for obj in query_set1:
           rankings.update({obj["target_id"]:1})
        query_set2 = graph_data[1]["fql_result_set"]
        places_list = []
        for target_id in rankings:
           count = rankings[target_id]
           for obj in query_set2:
              if(target_id == obj["page_id"]):
                 name = obj["name"]
                 number = obj["phone"]
                 place_id = obj["page_id"]
                 description = obj["description"]
                 places_list.append({"name":name, "number":number, "place_id":place_id, "description":description, "count":count})
        #url = 'http://text-processing.com/api/sentiment/'
        """for row in query_set1:
           values = {'text':row["message"].encode('utf-8')}
           data = urllib.urlencode(values)
           response = urllib2.urlopen(url, data)
           content = response.read()
           json_content = json.loads(content)
           prob = data["probability"]
           score = prob["pos"] - prob["neg"]
           rankings.update({row["checkin_id"]:score})
	"""
        return HttpResponse(json.dumps(places_list), mimetype="application/json")

def friendIntersectQuery(friends):
   query = "select uid2 from friend where uid1 = me()"
   for friend in friends:
      query = "SELECT uid1 FROM friend WHERE uid2=" + str(friend) + " AND uid1 in (" + query + ")"
   return query

@login_required(redirect_field_name="login/facebook")
def FacebookFriendsCheckinsIntersected(request):
    #friends = [223754, 203807]
    friends = request.GET.__getitem__('friends')
    if friends == '':
        friends = []
    else:
        friends = map(int,friends.split(','))
    print friends
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if(token):
        graph = facebook.GraphAPI(token)
        PLACE_TYPE = "RESTAURANT/CAFE"
        friends_query = friendIntersectQuery(friends)
        #return HttpResponse(json.dumps(friends_query), mimetype="application/json")
        friends = graph.fql(friends_query)
        print friends
        friend_list = []
        for friend in friends:
           friend_list.append(friend["uid1"])
        q1 = "select author_uid, coords, target_id, message, timestamp, checkin_id from checkin WHERE author_uid in("+ friends_query+")"
        queries = {"q1":q1,
"q2":"select name, phone, page_id, type, description, talking_about_count, were_here_count from page where type='RESTAURANT/CAFE' and page_id in (select target_id from #q1)",
"q3":"select uid, first_name, last_name from user where uid in (select author_uid from #q1)"}
        graph_data = graph.fql(queries)
        query_set1 = graph_data[0]["fql_result_set"]
        rankings = Counter()
        for obj in query_set1:
           rankings.update({obj["target_id"]:1})
        query_set2 = graph_data[1]["fql_result_set"]
        places_list = []
        for target_id in rankings:
           count = rankings[target_id]
           for obj in query_set2:
              if(target_id == obj["page_id"]):
                 name = obj["name"]
                 number = obj["phone"]
                 place_id = obj["page_id"]
                 description = obj["description"]
                 places_list.append({"name":name, "number":number, "place_id":place_id, "description":description, "count":count})
        #for row in query_set1:
           #values = {'text':row["message"].encode('utf-8')}
           #data = urllib.urlencode(values)
           #response = urllib2.urlopen(url, data)
           #content = response.read()
           #json_content = json.loads(content)
           #prob = data["probability"]
           #score = prob["pos"] - prob["neg"]
           #rankings.update({row["checkin_id"]:score})
        return HttpResponse(json.dumps(places_list), mimetype="application/json")

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

def FacebookLikesByUser(request, userID=''):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    if (userID == string.empty):
         userID = request.GET.get('userID', '')
    if (token) and (len(userID) > 0):
         graph = facebook.GraphAPI(token)
         query = "select music, books, tv, games from user where uid = " + userID
         data = graph.fql(query)
         return HttpResponse(json.dumps(data), mimetype="application/json")

def NewsTopics(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    users = request.GET.get('users', '')
    likes = list()
    if (token):
        graph = facebook.GraphAPI(token)
        query = "select music, books, tv, games, education, hometown_location from user where uid = me() or uid in (" + users + ")"
        data = graph.fql(query)
        schools_arr = list()
        for user in data:
	    music = user['music'].split(", ")
            likes = likes + music
            books = user['books'].split(", ")
            likes = likes + books
            tv = user['tv'].split(", ")
            likes = likes + tv
            games = user['games'].split(", ")
            likes = likes + games
            schools = user['education'] 
#            for school in schools:
#                name = school['school']['name']
#                likes.append(name)
#            hometown = user['hometown_location']
#            likes.append(hometown)
        likes = filter(None, likes)
        #likes.sort()
        grouped = [(topic, sum(1 for i in g)) for topic, g in groupby(likes)]
        #random.shuffle(grouped)
        sorted_results = sorted(grouped, key=lambda topic: topic[1]) 
        sorted_results.reverse()
        sorted_results = sorted_results[:100] 
        return HttpResponse(json.dumps(sorted_results), mimetype="application/json")
#        return HttpResponse(json.dumps(schools_arr), mimetype="application/json")
   
    return HttpResponse("Error", mimetype="application/json")

def Blekko(request):
    topic = request.GET.get('topic', '')
    news = list()
    html = urllib2.urlopen("http://blekko.com/ws/?q=" + urllib.quote(topic) + "+%2Fnews-magazine").read()
    return HttpResponse(html)

def BingNews(request):
    topic = (request.GET.get('topic', '')).encode('ascii', 'replace')
    news = list()
    request = urllib2.Request("https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%27news%27&Query=%27" + urllib.quote(topic) + "%27&Market=%27en-US%27&NewsSortBy=%27Date%27&$format=JSON")
    base64string = base64.encodestring('%s:%s' % ('', settings.BING_ACCOUNT_KEY)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string) 
    result = urllib2.urlopen(request)
    return HttpResponse(result, mimetype="application/json")

def Share(request):
    myUser = request.user
    instance = UserSocialAuth.objects.filter(provider='facebook').filter(user=myUser)
    tokens = [x.tokens for x in instance]
    token = tokens[0]["access_token"]
    graph = facebook.GraphAPI(token)
    graph.put_object("me", "feed", message="Testing wall posts.")
    return redirect("home.views.NewHome")

def SharePopup(request):
    url = "https://www.facebook.com/dialog/feed?app_id="
    url += settings.FACEBOOK_APP_ID
    url += "&link=https://ridemix.com"
    url += "&picture=http://static.ridemix.com/prod/media/logo.jpg"
    url += "&name=Ridemix"
    url += "&caption=Discover new places around you"
    url += "&description=Introducing a new, fun way for you and your friends to find new places you like, right from any mobile device!"
    url += "&redirect_uri=http://ridemix.com/new_home/"
    return redirect(url) 

def ParseLocations(possibleLocations, locations):
    result = []
    for location in locations:
	if(location["name"] in possibleLocations["name"]):
	    result.append(location)
    return result



