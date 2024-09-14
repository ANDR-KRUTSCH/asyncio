import aiohttp, datetime, asyncio, functools
from asgiref.sync import sync_to_async, async_to_sync

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.
async def get_url_details(session: aiohttp.ClientSession, url: str) -> dict:
    start_time = datetime.datetime.now()
    response = await session.get(url=url)
    response_body = await response.text()
    end_time = datetime.datetime.now()
    return dict(status=response.status, time=(end_time - start_time).microseconds, body_length=len(response_body))

async def make_requests(url: str, request_num: int) -> dict:
    async with aiohttp.ClientSession() as session:
        requests = [get_url_details(session=session, url=url) for _ in range(request_num)]
        results = await asyncio.gather(*requests, return_exceptions=True)
        failed_results = [str(result) for result in requests if isinstance(result, BaseException)]
        successful_results = [result for result in results if not isinstance(result, BaseException)]
        return dict(failed_results=failed_results, successful_results=successful_results)
    
async def requests_view(request: HttpRequest) -> HttpResponse:
    url: str = request.GET['url']
    request_num: int = request.GET['request_num']
    
    context = await make_requests(url=url, request_num=int(request_num))

    return render(request=request, template_name='async_api/requests.html', context=context)

# def requests_view_sync(request: HttpRequest) -> HttpResponse:
#     url: str = request.GET['url']
#     request_num: int = request.GET['request_num']
    
#     context = async_to_sync(functools.partial(make_requests, url, request_num))()

#     return render(request=request, template_name='async_api/requests.html', context=context)

# def sleep(seconds: int) -> None:
#     import time
#     time.sleep(seconds)

# async def sync_to_async_view(request: HttpRequest) -> HttpResponse:
#     sleep_time: int = int(request.GET['sleep_time'])
#     num_calls: int = int(request.GET['num_calls'])

#     thread_sensitive: bool = request.GET['thread_sensitive'] == 'True'
#     func = sync_to_async(functools.partial(sleep, sleep_time), thread_sensitive=thread_sensitive)
#     await asyncio.gather(*[func() for _ in range(num_calls)])
#     return HttpResponse(content='')