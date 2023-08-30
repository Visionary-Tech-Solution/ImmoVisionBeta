import requests,json,zipfile,os
from io import BytesIO
from rest_framework import serializers

#Default Serializer For any data provider

class PropertySerializer(serializers.Serializer):
    address = serializers.CharField(max_length= 3000)
    zipcode = serializers.CharField(max_length=200)
    price = serializers.IntegerField()
    image = serializers.URLField()
    zpid = serializers.CharField(max_length=400)
    origin = serializers.CharField(max_length = 100)
    lat = serializers.FloatField()
    long = serializers.FloatField()
    line1 = serializers.CharField()
    line2 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    listing_url = serializers.CharField()
    primary_photo_url = serializers.URLField()
    bedrooms = serializers.IntegerField()
    bathrooms = serializers.IntegerField()
    home_type = serializers.CharField()
    square_feet = serializers.CharField()
    price_currency = serializers.CharField()

class ImageSerializer(serializers.Serializer):
    images = serializers.JSONField()
    origin = serializers.CharField(max_length=200)


class Image:
    def __init__(self,images,origin) -> None:
        self.images = images
        self.origin = origin



#Default Class For any data Provider
class Property:
    def __init__(self,address,image,price,zpid,postalcode,origin,long=None,lat=None,line1=None,line2=None,listing_url=None,primary_photo_url=None,bedrooms=None,bathrooms=None,home_type=None,square_feet=None,city=None,price_currency=None,state=None) -> None:
        self.address = address+','+postalcode
        self.zipcode = postalcode
        self.price = price
        self.image = image
        self.zpid = zpid
        self.origin = origin
        self.long = long
        self.lat = lat
        self.line1 = line1
        self.line2 = line2
        self.listing_url = listing_url
        self.primary_photo_url = primary_photo_url
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.home_type = home_type
        self.square_feet = square_feet
        self.price_currency = price_currency
        self.city = city
        self.state = state

    def __str__(self) -> str:
        return self.address + '\n' + str(self.price) + '\n' + str(self.zpid)+'\n' + str(self.image) + '\n\n\n'



#Get Data From Zillow Provider
def get_data_from_zillow(id,zpid=None):
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
        bathrooms = i['bathrooms']
        line1 = i['address']['line1']
        line2 = i['address']['line2']
        city = i['address']['city']
        state = i['address']['stateOrProvince']
        address = line1+ ',' + city + ',' + state + ',' + line2
        long = i['longitude']
        lat = i['latitude']
        bedrooms = i['bedrooms']
        listing_url = i['listing_url']
        price_currency = i['price_currency']
        home_type = i['home_type']
        primary_photo_url = i['primary_photo_url']
        print(zpid)
        if zpid is not None:
            if str(i['zpid']) == zpid:
                objj = Property(address=address,image= i['primary_photo_url'],price = i['price'],zpid=str(i['zpid']),postalcode=i['address']['postalCode'],origin=origin,long=long,lat=lat,bedrooms=bedrooms,bathrooms=bathrooms,listing_url=listing_url,price_currency=price_currency,primary_photo_url=primary_photo_url,city=city,state=state,line1=line1,line2=line2,home_type=home_type)
                ser_data = PropertySerializer(objj)
                return ser_data.data
        obj.append(Property(address=address,image= i['primary_photo_url'],price = i['price'],zpid=str(i['zpid']),postalcode=i['address']['postalCode'],origin=origin,long=long,lat=lat,bedrooms=bedrooms,bathrooms=bathrooms,listing_url=listing_url,price_currency=price_currency,primary_photo_url=primary_photo_url,city=city,state=state,line1=line1,line2=line2,home_type=home_type))
        
    ser_data = PropertySerializer(obj,many=True)
    return ser_data.data




#get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a")

def get_data_from_realtor(id,profile_id,zpid=None):
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
        line1 = i['location']['address']['line']
        state = i['location']['address']['state']
        city = i['location']['address']['city']
        country = i['location']['address']['country']
        long = i['location']['address']['coordinate']['lon']
        lat = i['location']['address']['coordinate']['lat']
        primary_photo_url = i['primary_photo']['href']
        address = line1 + ',' + state+ ',' + city + ',' + country + ', Coordinate  long:' + str(long)+ ',lat:' + str(lat)
        listing_url = 'https://www.realtor.com/realestateandhomes-detail/'+i['permalink']
        bedrooms = i['description']['beds']
        bathrooms = i['description']['baths']
        sqft = i['description']['lot_sqft']
        home_type = i['description']['type']

        if zpid is not None:
            print(zpid)
            if i['permalink']==zpid:
                objj = Property(address=address,image= primary_photo_url,price = i['list_price'],zpid=i['permalink'],postalcode=i['location']['address']['postal_code'],origin=origin,line1=line1,state=state,city=city,long=long,lat=lat,bedrooms=bedrooms,bathrooms=bathrooms,listing_url=listing_url,primary_photo_url=primary_photo_url,home_type=home_type,square_feet=sqft)
                ser_data = PropertySerializer(objj)
                return ser_data.data
        obj.append(Property(address=address,image= primary_photo_url,price = i['list_price'],zpid=i['permalink'],postalcode=i['location']['address']['postal_code'],origin=origin,line1=line1,state=state,city=city,long=long,lat=lat,bedrooms=bedrooms,bathrooms=bathrooms,listing_url=listing_url,primary_photo_url=primary_photo_url,home_type=home_type,square_feet=sqft))
        
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
	    "X-RapidAPI-Key": "8555d72f83mshce016db2e8b1e44p171b67jsnb95dfe35b02a",
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
    return ser.data,img







#x = get_image_from_realtor('https://www.realtor.com/realestateandhomes-detail/11768-SW-245th-Ter_Homestead_FL_33032_M92527-64125')

