import re,time,vk_api

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
from pymongo import MongoClient


class Properties():
    def __init__(self):
        #Токен, ключ доступа
        self.token = ''
        #id группы
        self.groupId = '11233213'
        self.adminId = [1,111]

class Classificator():
    def __init__(self):
        #Пары корней слов для вопросов
        self.questionLib = [[["полож", "нахо", "полог", "адрес" , "ехат", "братьс", "йти", "ползт","попас", "дти"], ["музе", "органи", "клуб", "выстав", "зал", "завде", "здани","вас","вы"]],
                            [["работ", "откр","закр","граф","расп"], ["музе", "органи", "клуб", "выстав", "зал", "завде", "здани","вас","вы","как","когд","во скольк","работ"]],
                            [["стои", "купи" "поч", "цена", "брест"], ["музе", "билет", "посещен", "экскурс"] ],
                            [["что такое","чем"],["оранэл","оранел","музе"]]]

        #Фразы
        self.location = "Наш музей расположен по адресу:\n пр. Стачек, 91-А, Санкт-Петербург\n Проход пешком от станции метро Автово 1,1км 15 минут https://pp.userapi.com/c850324/v850324443/18b673/8uRZ-_lXi3E.jpg"
        self.worktime = "Наш музей работает с понедельника по пятницу с 10 до 19 часов"
        self.ticket = "Посещение нашего музея бесплатно.\nДля групп может быть оргинизована экскурсия по предварительной записи, стоимость экскурсии{price}"
        self.oranela = 'Оранэла - «Ораниенбаумская электрическая линия».\n\nЭто уникальная железнодорожная линия, созданная в Санкт-Петербурге в начале XX века вдоль Петергофской дороги, которая должна была связать Нарвскую заставу со Стрельной, Петергофом, Ораниенбаумом и Красной Горкой, общая длина составляет примерно 66 км). По сути, Ораниенбаумская электрическая линия — первый в Российской империи проект пригородных электропоездов'
        self.imbot = 'Я всего лишь машина, я не знаю ответа на этот вопрос, напишите "Ошибка" и Ваш вопрос будет отправден человеку'
        self.hello = 'Если у Вас есть вопросы к нам, вы можете задать их прямо здесь. Наш бот постарается ответить на него, если Вы не поучите ответ, сообщите об ошибке и наш модератор ответит Вам в ближайшее время'
        self.subscribeAdd = 'Спасибо за подписку)\nТеперь самые интересные новости будут приходить вам в личные сообщения'
        self.subscribeIs = 'Вы уже подписаны на новостные уведомления, если вы хотите отменить подписку, напишите "отменить подписку"'
        self.subscribeDel = 'Подписка на новости была отменена'
        self.subscribeErr = 'Сервис подписок временно недоступен'
        self.errMesA = 'REPORT\n----------\n{}\n{} {}\n'
        self.errMesU = 'Ваш вопрос был перенаправлен модератеру, ожидайте ответа на свой вопрос.\nСпасибо, что помогаете нам стать лучше'
        self.audiogide = 'Аудиогид по нашему музею можно послушать на сервисе IZITravel https://izi.travel/ru/8e2c-muzey-oranely'
        
        #Подключение к БД
        self.DBCon = MongoClient()
        self.MuseumColl = self.DBCon.MuseumMembers



    def keyboardQuestion(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Назад', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Сообщить об ошибке', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def keyboardMain(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Что такое Оранэла?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Расписание музея?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Адрес музея?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Сколько стоит билет?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Аудиоэкскурсия', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()
        
    def keyboardBack(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)
        return keyboard.get_keyboard()

    def treadQ(self,txt,lib):
        ga = False
        gb = False
        for i in lib[0]:
            if i in txt:
                ga = True
                break
        for i in lib[1]:
            if i in txt:
                gb = True
                break
        return ga*gb

    def isQuestion(self, txt):
        return(re.search(r'(\?|кто|по какому|что|како|который|где|когда|почему|зачем|куда|откуда|сколько|чей|как|можно ли|стоит ли|ли)',txt) != None)
    
    def startDialog(self,txt):
        return(re.search(r'(нача|меню|назад|старт|начн|бот|зада(.*)вопр|уточни|прив|ха(.*)й|здра(.*)ст)',txt) != None)
    
    def isAudioguide(self,txt):
        return(re.search(r'(аудио|электро|цифро|радио)(.*)(экскурс|гид)',txt) != None)

    def isSubscribe(self,txt):
        return(re.search(r'(.*)(подпис|уведом)(.*)',txt) != None)
    def isErrReport(self,txt):
        return(re.search(r'(ошиб|ответ|не(.*)отв|подробн)',txt) != None)

    def treadSubscribe(self,txt,userId):
        doc = { "vkId" : userId }
        mes = self.subscribeErr
        if 'отмен' in txt:
            self.MuseumColl.members.delete_one(doc)
            mes = self.subscribeDel
        else:
            if self.MuseumColl.members.find_one(doc) == None:
                if self.MuseumColl.members.insert_one(doc):
                    mes = self.subscribeAdd
            else:
                mes = self.subscribeIs
        return(mes)
            
    '''
    Номера вопросов
    0 - место музея
    1 - график работы
    2 - билет
    3 - оранэла
    etc
    '''

    def treadIt(self, txt,userId):
        mes = self.imbot
        keyboard = self.keyboardQuestion()
        if self.isQuestion(txt):
            keyboard = self.keyboardQuestion()
            numQ = -1
            status = False
            for i in range(len(self.questionLib)):
                status = self.treadQ(txt,self.questionLib[i])
                if status:
                    numQ = i
                    break
            if numQ == 0: mes = self.location
            elif numQ == 1: mes = self.worktime
            elif numQ == 2: mes = self.ticket
            elif numQ == 3: mes = self.oranela
        elif self.isAudioguide(txt):
            mes = self.audiogide
            keyboard = self.keyboardMain()
        elif self.isErrReport(txt):
            mes = 'Code1'
            keyboard = self.keyboardMain()
        elif self.startDialog(txt):
            keyboard = self.keyboardMain()
            mes = self.hello
        elif self.isSubscribe(txt):
            mes = self.treadSubscribe(txt, userId)
            keyboard = self.keyboardQuestion()
        return(mes, keyboard)
            
class VKGet(Properties):
    def initSession(self):
        vk_session = vk_api.VkApi(token=self.token)
        return(vk_session.get_api())
    def getUser(self,id):
        return(self.initSession().users.get(user_ids=id))
        
    
class Log(VKGet):
    def nowtime(self):
        return(time.strftime("%Y.%m.%d at %H:%M:%S:",time.localtime()))
    
    def logfilename(self):
        return('log'+ time.strftime("%Y%m%d",time.localtime()))

    def logRepost(self,obj):
        if obj.from_id > 0 and obj.owner_id > 0:
            fromUser = self.getUser(obj.from_id)
            ownerUser = self.getUser(obj.owner_id)

            mes = 'Repost wall No {} | from {} {} {} to {} {} {} at [ {} ]'.format(obj.copy_history[0]['id'],
                fromUser[0]['id'], fromUser[0]['first_name'], fromUser[0]['last_name'],
                ownerUser[0]['id'], ownerUser[0]['first_name'], ownerUser[0]['last_name'],
                self.nowtime())
            return(mes)
        return('GROUP REPOST TO PUBLIC')
    
    def logNewMes(self,obj):
        if obj.from_id > 0:
            fromUser = self.getUser(obj.from_id)

            mes = 'New message | from {} {} {} to our group at [ {} ]'.format(
                fromUser[0]['id'], fromUser[0]['first_name'], fromUser[0]['last_name'],
                self.nowtime())
        else:
            mes = 'New message | from group [{}] to our group at [ {} ]'.format( obj.from_id,self.nowtime() )
        return(mes)
        

    
    def log(self, type, obj):
        logid = self.logfilename()

        if type == VkBotEventType.WALL_REPOST:
            mes = self.logRepost(obj)
        elif type == VkBotEventType.MESSAGE_NEW:
            mes = self.logNewMes(obj)
        else:
            mes = 'Unknown type at[ {} ]'.format(self.nowtime())

        f = open(logid, 'a')
        f.write(mes)
        print('Repost add to logfile')
        return True
