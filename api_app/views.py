# from authentication.serializers import UserSerializerWithToken
import threading
import asyncio
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse,FileResponse
from .api_fetcher import *

from authentication.models import User
from account.models import Profile

@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_list_property(request):
    
    # user = request.user
    # qs = User.objects.filter(username=user.username)
    # if not qs.exists():
    #     return Response({"error": "Please Register First "})
    # current_user = qs.first()
    # profile = Profile.objects.get(user=current_user)
    
    data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998")
    data2 = get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a")
    data+=data2
    print(type(data))
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_image_list(request,zpid,origin):

    if origin=="zillow":
        data = get_image_from_zillow(zpid)
    elif origin=="realtor":
        data,zipfile = get_image_from_realtor('https://www.realtor.com/realestateandhomes-detail/'+zpid)

        return Response(data)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
    


def download_and_zip(request):
    async def download(request):
        download_file=[]
        z,img = get_image_from_realtor('https://www.realtor.com/realestateandhomes-detail/11768-SW-245th-Ter_Homestead_FL_33032_M92527-64125')
        for i in img:
            print(i)
            r = requests.get(i)
            if r.status_code == 200:
                download_file.append((os.path.basename(i),r.content))

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for filename, image_data in download_file:

                zf.writestr(filename+'.jpg', image_data)

        zip_buffer.seek(0)
        response = FileResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=images.zip'
        print(request)
        print(response)
        # Send the response
        return response
    # download_thread = threading.Thread(target=download, args=(request,))
    # download_thread.start()
    task = asyncio.create_task(download(request))
    return task

import aiohttp

from django.views import View
class DownloadAndZipView(View):
    async def download_images(self, request):
        try:
            # Fetch images from the external API
            z,image_urls =get_image_from_realtor('https://www.realtor.com/realestateandhomes-detail/11768-SW-245th-Ter_Homestead_FL_33032_M92527-64125')

            # Create a zip archive in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for url in image_urls:
                        tasks.append(self.download_image(session, zf, url))

                    await asyncio.gather(*tasks)

            # Create a response with the zip file
            zip_buffer.seek(0)  # Reset the buffer position
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=imagesss.zip'
            return response
        except Exception as e:
            print(f"An error occurred during download: {str(e)}")
            return None

    async def download_image(self, session, zip_archive, url):
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                filename = os.path.basename(url)

                # Determine the file extension based on the content type
                content_type = response.headers.get('content-type')
                if content_type == 'image/jpeg':
                    filename += '.jpg'
                elif content_type == 'image/png':
                    filename += '.png'
                else:
                    # Handle other image formats here
                    filename+='jpg'

                # Add the image data to the zip archive
                zip_archive.writestr(filename, image_data)

    async def get(self, request, *args, **kwargs):
        # Start the download process asynchronously
        r = await asyncio.create_task(self.download_images(request))

        # Return a response indicating that the download has started
        return r





@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_list_property_info(request,zpid,origin):
    
    # user = request.user
    # qs = User.objects.filter(username=user.username)
    # if not qs.exists():
    #     return Response({"error": "Please Register First "})
    # current_user = qs.first()
    # profile = Profile.objects.get(user=current_user)
    
    if origin=='realtor':
        data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998",zpid=zpid)

    elif origin=='zillow':
        data = get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a",zpid=zpid)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)
    print(type(data))
    if data:
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"error":"Something Went Wrong"},status=status.HTTP_400_BAD_REQUEST)