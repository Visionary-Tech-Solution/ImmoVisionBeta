import requests,json
from rest_framework import serializers

#Default Serializer For any data provider

class PropertySerializer(serializers.Serializer):
    address = serializers.CharField(max_length= 3000)
    zipcode = serializers.CharField(max_length=200)
    price = serializers.IntegerField()
    image = serializers.URLField()
    zpid = serializers.CharField(max_length=400)
    origin = serializers.CharField(max_length = 100)


class ImageSerializer(serializers.Serializer):
    images = serializers.JSONField()
    origin = serializers.CharField(max_length=200)


class Image:
    def __init__(self,images,origin) -> None:
        self.images = images
        self.origin = origin



#Default Class For any data Provider
class Property:
    def __init__(self,address,image,price,zpid,postalcode,origin) -> None:
        self.address = address+','+postalcode
        self.zipcode = postalcode
        self.price = price
        self.image = image
        self.zpid = zpid
        self.origin = origin

    def __str__(self) -> str:
        return self.address + '\n' + str(self.price) + '\n' + str(self.zpid)+'\n' + str(self.image) + '\n\n\n'



#Get Data From Zillow Provider
def get_data_from_zillow(id):
    url = "https://zillow-com1.p.rapidapi.com/agentActiveListings"
    querystring = {"zuid":id,"page":"1"}

    headers = {
        "X-RapidAPI-Key": "557f5a64d8msh55073d9d4d632d6p181dc1jsnf1235de7a1d8",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    origin  = "zillow"
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except:
        return False

    
    data = response.json()
    obj = []
    
    for i in data['listings']:
        address = i['address']['line1'] + ',' + i['address']['city'] + ',' + i['address']['stateOrProvince'] + ',' + i['address']['stateOrProvince'] + ',' + i['address']['line2']
        obj.append(Property(address=address,image= i['primary_photo_url'],price = i['price'],zpid=str(i['zpid']),postalcode=i['address']['postalCode'],origin=origin))
        
    ser_data = PropertySerializer(obj,many=True)
    return ser_data.data




#get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a")

def get_data_from_realtor(id,profile_id):
    url = "https://us-real-estate-listings.p.rapidapi.com/agent/listings"

    querystring = {"advertiser_id":id,"profile_url":profile_id}

    headers = {
        "X-RapidAPI-Key": "557f5a64d8msh55073d9d4d632d6p181dc1jsnf1235de7a1d8",
        "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
    }

    origin  = "realtor"
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except:
        return False

    
    data = response.json()
    for_sale = data['listings']['data']['forSale']
    #print(for_sale)
    obj = []
    
    for i in for_sale['results']:
        address = i['location']['address']['line'] + ',' + i['location']['address']['state'] + ',' + i['location']['address']['city'] + ',' + i['location']['address']['country'] + ', Coordinate  long:' + str(i['location']['address']['coordinate']['lon'])+ ',lat:' + str(i['location']['address']['coordinate']['lat'])
        obj.append(Property(address=address,image= i['primary_photo']['href'],price = i['list_price'],zpid=i['permalink'],postalcode=i['location']['address']['postal_code'],origin=origin))
        
    ser_data = PropertySerializer(obj,many=True)
    return ser_data.data

#data = get_data_from_realtor("1859437","https://www.realtor.com/realestateagents/Rhonda-Richie_ANCHORAGE_AK_2202468_150979998")


def get_image_from_zillow(zpid):
    url = "https://zillow-com1.p.rapidapi.com/images"
    querystring = {"zpid":zpid}
    headers = {
	    "X-RapidAPI-Key": "557f5a64d8msh55073d9d4d632d6p181dc1jsnf1235de7a1d8",
	    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except:
        return False
    data = response.json()
    data['origin'] = "Zillow"

    ser = ImageSerializer(data)
    return ser.data
    

def get_image_from_realtor(zpid):
    url = "https://us-real-estate-listings.p.rapidapi.com/v2/property"
    querystring = {"property_url":zpid}
    headers = {
	    "X-RapidAPI-Key": "557f5a64d8msh55073d9d4d632d6p181dc1jsnf1235de7a1d8",
	    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except:
        return False
    
    data = response.json()

    img = []
    try:
        image = data["data"]["photos"]
    except:
        image=[]
    try:
        community = data["data"]["community"]["photos"]
    except:
        community=[]
 
    for i in image:
        img.append(i['href'])

    for i in community:
        img.append(i['href'])
    obj = Image(img,"Realtor")
    ser = ImageSerializer(obj)
    return ser.data



