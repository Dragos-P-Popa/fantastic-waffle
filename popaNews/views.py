from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from rest_framework import status
from .models import Article
from .serializers import ArticleSerializer
from django.contrib.auth import authenticate, logout, login
from datetime import datetime

class Login(APIView):
    def post(self, request, *args, **kwargs):
        if request.content_type != "application/x-www-form-urlencoded":
            return Response('Expected application/x-www-form-urlencoded', status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get("username") is None or request.data.get("password") is None:
            return Response('Missing parameter', status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['username'] = username
            request.session.save()
            return Response('Success', status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        
class Logout(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            Session.objects.filter(session_key=request.session.session_key).delete()
            return Response('Success', status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ArticleView(APIView):
    def get(self, request, *args, **kwargs):
        expected_params = ["story_cat", "story_region", "story_date"]
        for param in expected_params:
            if request.GET.get(param) is None:
                return Response('Missing parameter', status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        articles = Article.objects.all()

        if articles.count() == 0:
            return Response('No articles found', status=status.HTTP_404_NOT_FOUND)

        if request.GET.get('story_cat') != '*':
            articles = articles.filter(category=request.GET.get('story_cat'))
        if request.GET.get('story_region') != '*':
            articles = articles.filter(region=request.GET.get('story_region'))
        if request.GET.get('story_date') != '*':
            articles = articles.filter(date__gte=datetime.strptime(request.GET.get('story_date'), '%Y-%m-%d'), date__lte=datetime.today().strftime('%Y-%m-%d'))
        
        serializer = ArticleSerializer(articles, many=True)
        responseData = {'stories': serializer.data}
        return Response(responseData, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated is False:
            return Response('Unauthorized', status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if request.content_type != "application/json":
            return Response('Expected application/json', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        expected_params = ["category", "headline", "region", "details"]
        for param in expected_params:
            if request.data.get(param) is None:
                return Response('Missing parameter', status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        if request.data.get("category").upper() not in ['POL', 'ART', 'TECH', 'TRIVIA']:
            return Response('Invalid category', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        if request.data.get("region").upper() not in ['UK', 'EU', 'W']:
            return Response('Invalid region', status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        article = Article(category=request.data.get('category'), headline=request.data.get('headline'), region=request.data.get('region'), details=request.data.get('details'), author=request.user)
        article.save()

        return Response('Article saved', status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated is False:
            return Response('Unauthorized', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        if self.kwargs['story'] is None:
            return Response('Missing parameter', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try: 
            deleted = Article.objects.filter(key=self.kwargs['story']).delete() # 200 even when nothing is deleted / key does not exist
            count = deleted[0]
            
            if count == 0:
                return Response('Story id ' + self.kwargs['story'] + ' found', status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            return Response('Story deleted', status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_503_SERVICE_UNAVAILABLE)