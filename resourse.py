import re,time

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from pymongo import MongoClient


class Properties():
    def __init__(self):
        #Токен, ключ доступа
        self.token = 'токен'
        #id группы
        self.groupId = 'id группы'
        #id админов
        self.adminId = [2,3,4]

class Classificator():
    def __init__(self):
        #Пары корней слов для вопросов
        self.questionLib = [[["полож", "нахо", "полог", "адрес" , "ехат", "братьс", "йти", "ползт","попас", "дти"], ["музе", "органи", "клуб", "выстав", "зал", "завде", "здани","вас","вы"]],
                            [["работ", "откр","закр","граф","расп"], ["музе", "органи", "клуб", "выстав", "зал", "завде", "здани","вас","вы","как","когд","во скольк","работ"]],
                            [["стои", "купи" "поч", "цена", "брест"], ["музе", "билет", "посещен", "экскурс"] ],
                            [["что такое","чем"],[,"музе"]]]

        #Фразы
        self.location = "Наш музей расположен по адресу:\n Ул простая\n Проход пешком от станции метро Метрошная 1,1км 15 минут"
        self.worktime = "Наш музей работает с понедельника по пятницу с 11 д12 часов"
        self.ticket = "Посещение нашего музея бесплатно.\nДля групп может быть оргинизована экскурсия по предварительной записи, стоимость экскурсии{price}"
        self.oranela = 'Музей классный'
        self.imbot = 'Я всего лишь машина, я не знаю ответа на этот вопрос, напишите "Ошибка" и Ваш вопрос будет отправден человеку'
        self.hello = 'Если у Вас есть вопросы к нам, вы можете задать их прямо здесь. Наш бот постарается ответить на него, если Вы не поучите ответ, сообщите об ошибке и наш модератор ответит Вам в ближайшее время'
        self.subscribeAdd = 'Спасибо за подписку)\nТеперь самые интересные новости будут приходить вам в личные сообщения'
        self.subscribeIs = 'Вы уже подписаны на новостные уведомления, если вы хотите отменить подписку, напишите "отменить подписку"'
        self.subscribeDel = 'Подписка на новости была отменена'
        self.subscribeErr = 'Сервис подписок временно недоступен'
        self.errMesA = 'REPORT\n----------\n{}\n{} {}\n'
        self.errMesU = 'Ваш вопрос был перенаправлен модератеру, ожидайте ответа на свой вопрос.\nСпасибо, что помогаете нам стать лучше'
        self.audiogide = 'Аудиогид по нашему музею можно послушать на сервисе IZITravel link.link'
        
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
        keyboard.add_button('Что такое музей?', color=VkKeyboardColor.PRIMARY)
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
    3 - музей
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
            
