import requests,json
from rest_framework import serializers

#Default Serializer For any data provider

class PropertySerializer(serializers.Serializer):
    address = serializers.CharField(max_length= 3000)
    zipcode = serializers.CharField(max_length=200)
    price = serializers.IntegerField()
    image = serializers.URLField()
    zpid = serializers.IntegerField()


#Default Class For any data Provider
class Property:
    def __init__(self,address,image,price,zpid,postalcode) -> None:
        self.address = address+','+postalcode
        self.zipcode = postalcode
        self.price = price
        self.image = image
        self.zpid = zpid

    def __str__(self) -> str:
        return self.address + '\n' + str(self.price) + '\n' + str(self.zuid)+'\n' + str(self.image) + '\n\n\n'



#Get Data From Zillow Provider
def get_data_from_zillow(id):
    url = "https://zillow-com1.p.rapidapi.com/agentActiveListings"

    querystring = {"zuid":id,"page":"1"}

    headers = {
        "X-RapidAPI-Key": "557f5a64d8msh55073d9d4d632d6p181dc1jsnf1235de7a1d8",
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except:
        return False

    
    data = response.json()
    obj = []
    
    for i in data['listings']:
        address = i['address']['line1'] + ',' + i['address']['city'] + ',' + i['address']['stateOrProvince'] + ',' + i['address']['stateOrProvince'] + ',' + i['address']['line2']
        obj.append(Property(address=address,image= i['primary_photo_url'],price = i['price'],zpid=i['zpid'],postalcode=i['address']['postalCode']))
        
    ser_data = PropertySerializer(obj,many=True)
    return ser_data.data




#get_data_from_zillow("X1-ZUytn1phpg9b7t_5i26a")