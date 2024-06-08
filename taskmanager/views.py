import uuid
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .task import scrape_coin_data
import redis
import json
from .models import TaskResult

# Configure Redis connection
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class StartScrapingView(APIView):
    def post(self, request):
        coin_acronyms = request.data.get('coins', [])
        if not coin_acronyms:
            return Response({"error": "No coin acronyms provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        job_id = str(uuid.uuid4())
        tasks_list = []
        
        for acronym in coin_acronyms:
            print(str(acronym).lower())
            task = scrape_coin_data(str(acronym).lower())
            tasks_list.append(task)

        data = {'job_id': job_id, 'tasks': tasks_list}
        result = TaskResult.objects.create(job_id=job_id, result=json.dumps(data))
        result.save()
        # redis_client.set(job_id, json.dumps(data))
        return Response({'job_id': job_id},status=status.HTTP_202_ACCEPTED)

class ScrapingStatusView(APIView):
    def get(self, request, job_id):
        # data = redis_client.get(job_id)
        task_result = TaskResult.objects.get(job_id=job_id)
        if task_result is None:
            return Response({"error": "Job ID not found or data not available."}, status=status.HTTP_404_NOT_FOUND)
        
        # return Response(json.loads(data), status=status.HTTP_200_OK)
        return Response(json.loads(task_result.result), status=status.HTTP_200_OK)
