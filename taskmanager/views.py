import uuid
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .task import scrape_coin_data
import redis
import json
from .models import TaskResult
from pandas.io.json import _normalize
from io import BytesIO
import pandas as pd
from django.http import HttpResponse

def transform_data(json_data):
    transformed_data = []
    for task in json_data['tasks']:
        output = task['output']
        contracts = output.get('Contracts', [])
        official_links = output.get('Official links', [])
        socials = output.get('Socials', [])
        
        data = {
            'job_id': json_data['job_id'],
            'price': output.get('price', ''),
            'price_change': output.get('price_change', ''),
            'market_cap': output.get('market_cap', ''),
            'volume': output.get('volume', ''),
            'volume_market_cap': output.get('volume_market_cap', ''),
            'circulating_supply': output.get('circulating_supply', ''),
            'total_supply': output.get('total_supply', ''),
            'max__supply': output.get('max__supply', ''),
            'fully_diluted_market_cap': output.get('fully_diluted_market_cap', ''),
            'market_cap_rank': output.get('market_cap_rank', ''),
            'volume_rank': output.get('volume_rank', ''),
            'Contracts': ', '.join([f"{contract['name']}: {contract['address']}" for contract in contracts]),
            'Official_links': ', '.join([f"{link['name']}: {link['url']}" for link in official_links]),
            'Socials': ', '.join([f"{social['name']}: {social['url']}" for social in socials]),
            'coin': task.get('coin', '')
        }
        
        transformed_data.append(data)
    return transformed_data

def json_to_excel(json_data):
    data = transform_data(json_data)
    df = pd.DataFrame(data)
    return dump_to_excel(df, 'task_result')

def dump_to_excel(dataframe, file_name):
    """Write pandas dataframe to excel sheet.

    Args:
        dataframe (DataFrame): pandas dataframe

    Returns:
        bytes: excel sheet bytes
    """
    with BytesIO() as bio:
        writer = pd.ExcelWriter(
            bio, engine="xlsxwriter", date_format="dd-mm-yyyy"
        )

        # df_total is the data frame that we want to write into excel.
        dataframe.reset_index(drop=True, inplace=False)
        dataframe.index += 1
        dataframe.to_excel(writer, sheet_name=file_name, index=False)
        writer.close()

        bio.seek(0)
        return bio.getvalue()

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

class ScrapingStatusDownloadView(APIView):
    def get(self, request, job_id):
        
        task_result = TaskResult.objects.get(job_id=job_id)
        data = json.loads(task_result.result)

        if task_result is None:
            return Response({"error": "Job ID not found or data not available."}, status=status.HTTP_404_NOT_FOUND)
        
        workbook = json_to_excel(data)
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response = HttpResponse(workbook, content_type=content_type)
        response["Content-Disposition"] = f"attachment; filename=task_result.xlsx"
        return response