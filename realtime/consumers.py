from channels.consumer import SyncConsumer,AsyncConsumer

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self,event):
        print("Websocket Connected ....")




    def websocket_receive(self,event):
        print("Message Received....")



    def websocket_disconnect(self,event):
        print("Websocket Disconnect ....")

        