import json
from channels.generic.websocket import WebsocketConsumer
from esurvey.models import VAD, Session, Speech
import datetime
from django.contrib.auth.models import User




class DataConsumer(WebsocketConsumer):
    VAD_OBJECTS =[]
    SPEECH_OBJECTS =[]
    VAD_LIMIT_WRITE = 2
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s'%self.room_name
        self.accept()

    def disconnect(self, close_code):
        if len(self.VAD_OBJECTS) > 0:
            self.writeVAD(self.VAD_OBJECTS)
            self.VAD_OBJECTS = []
        if len(self.SPEECH_OBJECTS) > 0:
            self.writeSPEECH(self.SPEECH_OBJECTS)
            self.SPEECH_OBJECTS = []

    def writeVAD(self,vad_objs):
        objs = VAD.objects.bulk_create(vad_objs)

    def writeSPEECH(self,speech_objs):
        objs = Speech.objects.bulk_create(speech_objs)


    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        print('Data received',text_data_json)
        session = text_data_json["session"]
        user = text_data_json["user"]
        group = text_data_json["group"]
        strDate = text_data_json["strDate"]
        speech = text_data_json["speech"]
        activity = text_data_json["activity"]
        dt = datetime.datetime.fromtimestamp(float(strDate))
        print('DATE:',dt)
        session_obj = Session.objects.get(pk=int(session))
        user_obj = User.objects.get(pk=int(user))
        self.VAD_OBJECTS.append(VAD(session=session_obj,user=user_obj,group=int(group),timestamp=dt,activity=activity))
        self.SPEECH_OBJECTS.append(Speech(session=session_obj,user=user_obj,group=int(group),timestamp=dt,TextField=speech))
        print('VAD OBJECTS Length:',len(self.VAD_OBJECTS))
        if len(self.VAD_OBJECTS) > self.VAD_LIMIT_WRITE:
            self.writeVAD(self.VAD_OBJECTS)
            self.VAD_OBJECTS = []

        if len(self.SPEECH_OBJECTS) > self.VAD_LIMIT_WRITE:
            self.writeSPEECH(self.SPEECH_OBJECTS)
            self.SPEECH_OBJECTS = []

        """
        message = text_data_json['message']

        print(message)
        self.send(text_data=json.dumps({
            'message': message
        }))
        """
