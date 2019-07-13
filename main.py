import vk_api, re
import time
from resource import Properties, Classificator

Prop = Properties()
Controller = Classificator()


from pymongo import MongoClient

#Подключение
MongoDBConnection = MongoClient()
#Коллекция
MongoDBOranela = MongoDBConnection.oranelaMembers

from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

def log(obj):
    nowTime = time.strftime("%Y.%m.%d at %H:%M:%S:",time.localtime())
    logid = 'log'+ time.strftime("%Y%m%d",time.localtime())

    mes = 'From {} | Type: mes | [{}]\n'.format(obj.from_id, nowTime)
    f = open(logid, 'a')
    f.write(mes)
    print('Mess add to logfile')
    return True

#Лог о репорте
def logErr(obj):
    nowTime = time.strftime("%Y.%m.%d at %H:%M:%S:",time.localtime())
    logid = 'log'+ time.strftime("%Y%m%d",time.localtime())

    mes = 'Err REPORT From {} | Type: mes | [{}]\n'.format(obj.from_id, nowTime)
    f = open(logid, 'a')
    f.write(mes)
    print('Err RPORT add to logfile')
    return True

def main():
    vk_session = vk_api.VkApi(token=Prop.token)
    vk = vk_session.get_api()
    #upload = VkUpload(vk_session)
    longpoll = VkBotLongPoll(vk_session, Prop.groupId)
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            event.obj.text = event.obj.text.lower()

            mes, keyboard = Controller.treadIt(event.obj.text, event.obj.from_id)
            if mes == 'Code1':
                vk.messages.send(
                    peer_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard = keyboard,
                    message=Controller.errMesU
                )
                info = vk.users.get(user_ids=event.obj.from_id)
                for id in Prop.adminId:
                    vk.messages.send(
                        peer_id=id,
                        random_id=get_random_id(),
                        keyboard = keyboard,
                        message=Controller.errMesA.format(info[0]['id'],info[0]['first_name'],info[0]['last_name'])
                    )
                logErr(event.obj)
            else:
                log(event.obj)
                vk.messages.send(
                    peer_id=event.obj.from_id,
                    random_id=get_random_id(),
                    keyboard = keyboard,
                    message=mes
                )

            print('Новое сообщение!')
        else:
            print(event.type)


if __name__ == '__main__':
    main()
