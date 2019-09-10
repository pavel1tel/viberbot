from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.messages.keyboard_message import KeyboardMessage
from datetime import datetime
from bot import app, db, viber
from .model import User, Query, Zakaz, NP, Search
import time
import requests
import logging
import sched
import threading
import json
import os
import pytz

OWNER_ID =os.environ.get('OWNER_ID') or "stabVf6hC1w8nbEV2hPU8g=="


@app.route('/exc', methods=['GET'])
def test_exc():
    raise Exception('Test Exception')
    return Response(status=200)

@app.route('/', methods=['POST'])
def incoming():

        def back_to_menu(db,quer,viber,delete_zakaz=True):
            quer.query_number = 'm2'
            if delete_zakaz:
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id ).first()
                num = int(quer.zakaz_num)-1
                if Zakaz.query.filter_by(user=usr).all():
                    for i in range(num+1):
                        zkz = Zakaz.query.filter_by(user=usr).all()[0]
                        db.session.delete(zkz)
                quer.zakaz_num = 1
            db.session.commit()
            with open('./bot/buttons_conf/1menu_button.json') as f:
                 button = json.load(f)
            viber.send_messages(viber_request.sender.id , [
                 TextMessage(None,None,'Здравствуйте, я помощник Юлии - вашего поставщика. Чем я могу вам помочь?'),
                 KeyboardMessage(keyboard = button),
                    ])
            return Response(status=200)


        viber_request = viber.parse_request(request.get_data().decode('utf8'))
        if isinstance(viber_request, ViberMessageRequest):

            usr = User.query.filter_by(user_viber_id=viber_request.sender.id ).first()
            quer = Query.query.filter_by(user=usr).first()
            try:
                np = NP.query.filter_by(user = usr).first()
                if np == None:
                    del np
            except:
                pass
            num = int(quer.zakaz_num) - 1             
            if viber_request.message.__getattribute__('text') == "Вернутся на главное меню":
                back_to_menu(db,quer,viber) 

            if quer.query_number=='m1' :
                quer.query_number = 'm2'
                db.session.commit()
                with open('./bot/buttons_conf/1menu_button.json') as f:
                    button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Здравствуйте, я помощник Юлии - вашего поставщика. Чем я могу вам помочь?'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status=200)                    

            if viber_request.message.__getattribute__('text')=='/reset':
                back_to_menu(db,quer,viber) 
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id ).first()
                novap = NP.query.filter_by(user=usr).first()
                if novap:
                    db.session.delete(novap)
                    db.session.commit()
                src = Search.query.filter_by(user = usr)
                if src:
                    src.delete()
                    db.session.commit()
                return Response(status=200)

            if quer.query_number == 'm2':
                if viber_request.message.__getattribute__('text')=='Zakaz':
                     with open('./bot/buttons_conf/2menu_button.json') as f:
                        button = json.load(f)
                     viber.send_messages(viber_request.sender.id, [
                        TextMessage(None,None,'Выберите производителя'),
                        KeyboardMessage(keyboard = button),
                      ])
                     quer.query_number= 'm3'
                     usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                     zkz = Zakaz(user = usr)
                     db.session.add(zkz)
                     db.session.commit()
                     return Response(status=200)

                elif viber_request.message.__getattribute__('text')=="Track":
                    quer.query_number = 'trac'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Введите номер ТТН, который вы хотите отследить')
                        ])
                    return Response(status=200)
        
            if quer.query_number == 'trac':
                with open('./bot/np_sample/tracking.json') as file:
                    sample_file = json.load(file)
                sample_file['methodProperties']['Documents'][0]['DocumentNumber'] = viber_request.message.__getattribute__('text')
                response = requests.post('https://api.novaposhta.ua/v2.0/json/', data = json.dumps(sample_file))
                status = response.json()['data'][0]['Status']
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Статус вашей посылки: ' + status)
                    ])
                back_to_menu(db,quer,viber,False)
                return Response(status=200)


            if quer.query_number == 'm3':
                if viber_request.message.__getattribute__('text')not in ['Zakaz','Track']:
                    quer.query_number = 'm4'
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                    zkz = Zakaz.query.filter_by(user= usr)[num]
                    zkz.provider = viber_request.message.__getattribute__('text')
                    if not zkz.provider:
                        quer.query_number = 'm3'
                        with open('./bot/buttons_conf/2menu_button.json') as f:
                            button = json.load(f)
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(None,None,'Выберите производителя'),
                            KeyboardMessage(keyboard = button),
                        ])
                        db.session.commit()
                        return Response(status=200)

                    if viber_request.message.__getattribute__('text') == "Цепочки":
                        quer.query_number = 'm5'
                        zkz.type = "Цепочка"
                        viber.send_messages(viber_request.sender.id , [
                            TextMessage(None,None, 'Напишите наименование (артикул) изделия')
                            ])
                        db.session.commit()
                        return Response(status=200)
                    db.session.commit()
                    with open('./bot/buttons_conf/3menu_button.json') as f:
                        button = json.load(f)
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Что именно вы хотите заказать?'),
                        KeyboardMessage(keyboard = button),
                        ])
                    return Response(status=200)
                
                
                
                
            if quer.query_number == 'm4':
                quer.query_number = 'm5' 
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                zkz = Zakaz.query.filter_by(user= usr)[num]
                zkz.type = viber_request.message.__getattribute__('text')
                if not zkz.type:
                    quer.query_number = 'm4'
                    with open('./bot/buttons_conf/3menu_button.json') as f:
                        button = json.load(f)
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Что именно вы хотите заказать?'),
                        KeyboardMessage(keyboard = button),
                        ])
                    db.session.commit()
                    return Response(status=200)
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Напишите наименование (артикул) изделия')
                    ])

                return Response(status=200)

            if quer.query_number == 'm5':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                zkz = Zakaz.query.filter_by(user= usr)[num]
                zkz.name = viber_request.message.__getattribute__('text')
                db.session.commit()
                    
                if zkz.type in ['Кольцо', 'Набор', 'Браслет', 'Цепочка']:
                    quer.query_number = 'm6'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Напишите размер изделия')
                        ])
                    return Response(status=200)

                elif zkz.type in ['Серьги', 'Подвес']:
                    quer.query_number = 'm7'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Напишите цвет изделия или отправьте фото. Если изделие без камней, просто поставьте прочерк')
                        ])
                    return Response(status=200)

            if quer.query_number == 'm6':
                quer.query_number = 'm7'
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                zkz = Zakaz.query.filter_by(user= usr)[num]
                zkz.size = viber_request.message.__getattribute__('text')
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Напишите цвет изделия или отправте фото. Если изделие без камней, просто поставьте прочерк')
                    ])
                return Response(status=200)

            if quer.query_number == 'm7':
                quer.query_number = 'm8'
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                zkz = Zakaz.query.filter_by(user= usr)[num]
                try:
                    zkz.color= viber_request.message.__getattribute__('media')
                except:
                    zkz.color = viber_request.message.__getattribute__('text')
                db.session.commit()
                with open('./bot/buttons_conf/4menu_button.json') as f:
                    button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Хотите ли вы добавить еще товар к этому заказу?'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status=200)
            if quer.query_number == 'm8':
                if viber_request.message.__getattribute__('text') == 'Yes':
                    quer.query_number = 'm3'
                    with open('./bot/buttons_conf/2menu_button.json') as f:
                         button = json.load(f)
                    viber.send_messages(viber_request.sender.id , [
                         TextMessage(None,None,'Выберите п производителя'),
                         KeyboardMessage(keyboard = button),
                            ])
                    quer.zakaz_num += 1
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                    zkz = Zakaz(user = usr)
                    db.session.add(zkz)
                    db.session.commit()
                    return Response(status=200)
                elif viber_request.message.__getattribute__('text') == 'No':
                    quer.query_number = 'b1'
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first() 
                    np = NP(user = usr)
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Напишите город получателя')
                        ])
                    return Response(status= 200)
            if quer.query_number == 'b1' and viber_request.message.__getattribute__('text') != np.city:
                np.city = viber_request.message.__getattribute__('text')
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Напишите порядковый номер города')
                    ])
                with open('./bot/np_sample/find-citi.json') as file:
                    sample_file = json.load(file)
                sample_file['methodProperties']['FindByString'] = viber_request.message.__getattribute__('text')
                response = requests.post('https://api.novaposhta.ua/v2.0/json/', data = json.dumps(sample_file))
                i = 1
                for city in response.json()["data"]:
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                    description = city['DescriptionRu']
                    ref = city['Ref']
                    src = Search(number = i,
                                description = description,
                                ref = ref,
                                user = usr)
                    i += 1
                    db.session.add(src)
                quer.query_number = 'm9'
                db.session.commit()
                scr = Search.query.filter_by(user=usr)
                i = 1
                for city in scr:
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, f'{i}. {city.description}')
                        ])
                    i += 1
                return Response(status = 200)
            
            if quer.query_number == 'm9':
                city_number = viber_request.message.__getattribute__('text')
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                src = Search.query.filter_by(user=usr, number = city_number).first()
                try:
                    np.city = src.ref
                except:
                    viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Неправильно указан город')
                        ])
                Search.query.filter_by(user=usr).delete()
                quer.query_number = 'm10'
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Укажите отделение Новой Почты')
                    ])
                return Response(status= 200)

            if quer.query_number == 'm10':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                with open('./bot/np_sample/find_adress.json') as file:
                    sample_file = json.load(file)
                sample_file['methodProperties']['CityRef'] = np.city
                response = requests.post('https://api.novaposhta.ua/v2.0/json/', data = json.dumps(sample_file))
                adr = viber_request.message.__getattribute__('text')
                for otdel in response.json()['data']:
                    if otdel['Number'] == str(adr):
                        np.adress = otdel['Ref']
                quer.query_number = 'm11'
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Напишите номер телефона получателя. В формате 380.....')
                    ])
                return Response(status= 200)
            
            if quer.query_number == 'm11':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.phone_number = viber_request.message.__getattribute__('text').replace(" ", "").replace("+","")
                quer.query_number = 'm12'
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Напишите ФИО получателя')
                    ])
                return Response(status= 200)
            if quer.query_number == 'm12':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.recip_name = viber_request.message.__getattribute__('text')
                quer.query_number = 'm13'
                db.session.commit()
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Укажите оценочную стоимость заказа')
                    ])
                return Response(status= 200)

            if quer.query_number == 'm13':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.price = viber_request.message.__getattribute__('text')
                quer.query_number = 'm14'
                db.session.commit()
                with open('./bot/buttons_conf/5menu_button.json') as f:
                     button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Выберите способ оплаты'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status= 200)

            if quer.query_number == 'm14':
                if viber_request.message.__getattribute__('text')=='ПриватБанк':
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                    np = NP.query.filter_by(user=usr).first()
                    np.type = 'ПриватБанк'
                    quer.query_number = 'm15'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Напишите сумму, которую вы зачислите на карту')
                        ])
                    return Response(status= 200)
                if viber_request.message.__getattribute__('text')=='Наложенный платеж':
                    usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                    np = NP.query.filter_by(user=usr).first()
                    np.type = 'Наложеный платеж'
                    quer.query_number = 'm17'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Напишите суму наложенного платежа')
                        ])

                    return Response(status=200)

            if quer.query_number == 'm15':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.oplata_card = viber_request.message.__getattribute__('text')
                quer.query_number = 'y1'
                db.session.commit()
                with open('./bot/buttons_conf/6menu_button.json') as f:
                     button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Кто оплачивает услуги доставки'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status= 200)
            if quer.query_number == 'y1':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.oplata_dostavki = viber_request.message.__getattribute__('text')
                quer.query_number = 'y2'
                db.session.commit()
                with open('./bot/buttons_conf/4menu_button.json') as f:
                     button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Есть комментарии к заказу?'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status=200)
            if quer.query_number == 'y2':
                if viber_request.message.__getattribute__('text') == 'Yes':
                    quer.query_number = 'y3'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Напишите ваши пожелания')
                        ])
                    return Response(status=200)
            
                if viber_request.message.__getattribute__('text') == 'No':
                    quer.query_number = 'm16'
                    db.session.commit()

            if quer.query_number == 'y3':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.region = viber_request.message.__getattribute__('text')
                quer.query_number = 'm16'
                db.session.commit()
                
            if quer.query_number == 'a':
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    if not zkz.type :
                        zkz.type = viber_request.message.__getattribute__('text')
                        quer.query_number = 'm16'
                        db.session.commit()
                        return Response(status=200)
                                        
            if quer.query_number == 'b':
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    if not zkz.provider :
                        zkz.provider = viber_request.message.__getattribute__('text')
                        quer.query_number = 'm16'
                        db.session.commit()
                        return Response(status=200)
                                        
            if quer.query_number == 'c':
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    if not zkz.name :
                        zkz.name = viber_request.message.__getattribute__('text')
                        quer.query_number = 'm16'
                        db.session.commit()
                        return Response(status=200)
                                        
            if quer.query_number == 'd':
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    if not zkz.color :
                        zkz.color = viber_request.message.__getattribute__('text')
                        quer.query_number = 'm16'
                        db.session.commit()
                        return Response(status=200)

             
            if quer.query_number == 'm16':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    if not zkz.type or zkz.type == "Zakaz" :
                        with open('./bot/buttons_conf/3menu_button.json') as f:
                            button = json.load(f)
                        viber.send_messages(viber_request.sender.id , [
                            TextMessage(None,None, f'Уточните пожалуйста еще раз тип {i} заказа'),
                            KeyboardMessage(keyboard = button),
                            ])
                        quer.query_number = 'a'
                        db.session.commit()
                        return Response(status=200)
                                        
                    elif not zkz.provider or zkz.provider == "Zakaz" :
                        with open('./bot/buttons_conf/2menu_button.json') as f:
                            button = json.load(f)
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(None,None,f'Уточните производителя {i} заказа пожалуйста'),
                            KeyboardMessage(keyboard = button),
                        ])
                        quer.query_number = 'b'
                        db.session.commit()
                        return Response(status=200)
                                        
                    elif not zkz.name or zkz.name == "Zakaz":
                        viber.send_messages(viber_request.sender.id , [
                            TextMessage(None,None, f'Уточните пожалуйста артикул {i} заказа еще раз')
                            ])
                        quer.query_number = 'с'
                        db.session.commit()
                        return Response(status=200)
                                        
                    if not zkz.color or zkz.color == "Zakaz" :
                        viber.send_messages(viber_request.sender.id , [
                            TextMessage(None,None, f'Уточните цвет изделия или отправте фото {i} заказа')
                            ])
                        quer.query_number = 'd'
                        db.session.commit()
                        return Response(status=200)
                                        
                with open('./bot/np_sample/create_person.json') as file:
                        sample_file = json.load(file)
                name = np.recip_name.split(" ")
                try:
                    sample_file["methodProperties"]["FirstName"] = name[1]
                    sample_file["methodProperties"]["LastName"] = name[0]
                except:
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Допущена ошибка в введении имени получателя. Напишите /reset и заполните все сначала')
                        ])
                try:
                    sample_file["methodProperties"]["MiddleName"] = name[2]
                except:
                    pass
                sample_file["methodProperties"]["Phone"] = np.phone_number
                response = requests.post('https://api.novaposhta.ua/v2.0/json/', data = json.dumps(sample_file))
                try:
                    np.recip_name = response.json()['data'][0]["Ref"]
                    np.area = response.json()['data'][0]['ContactPerson']['data'][0]["Ref"]
                except:
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Допущена ошибка в введении данных получателя. Напишите /reset и заполните все сначала')
                        ])
                db.session.commit()
                if np.type == 'Наложеный платеж':
                    with open('./bot/np_sample/naloj-send.json') as file:
                        sample_file = json.load(file)
                    sample_file['methodProperties']['BackwardDeliveryData'][0]['RedeliveryString'] = str(np.oplata_nalojeniy)
                else:    
                    with open('./bot/np_sample/card-send.json') as file:
                        sample_file = json.load(file)
                sample_file['methodProperties']['Cost'] = str(np.price) 
                sample_file['methodProperties']['CityRecipient'] = str(np.city) 
                sample_file['methodProperties']['Recipient'] = str(np.recip_name) 
                sample_file['methodProperties']['RecipientAddress'] = str(np.adress) 
                sample_file['methodProperties']['ContactRecipient'] = str(np.area) 
                sample_file['methodProperties']['RecipientsPhone'] = str(np.phone_number) 
                sample_file['methodProperties']['RecipientsPhone'] = str(np.phone_number) 
                sample_file['methodProperties']['PayerType'] = str(np.oplata_dostavki) 
                tzkiev = pytz.timezone('Europe/Kiev')
                today = datetime.now(tzkiev)
                sample_file['methodProperties']['DateTime'] = today.strftime("%d.%m.%Y")
                response = requests.post('https://api.novaposhta.ua/v2.0/json/', data = json.dumps(sample_file))
                try:
                    print(response.json())
                    #ttn = response.json()["data"][0]['IntDocNumber']
                except: 
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Допущена ошибка в введении данных Новой Почты. Напишите /reset и заполните все сначала')
                        ])
                    return Response(status=200)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None, 'Спасибо за заказ! Номер ТТН: ' + str(ttn) + '. Номер станет активным после отправки заказа. Отследить статус посылки вы можете воспользовавшись кнопкой «Отследить ТТН»')
                    ])
                message = f"Заказ от {usr.nickname} : \n\n"
                for i in range(num+1):
                    zkz = Zakaz.query.filter_by(user = usr).all()[i]
                    mm = f"{i+1}. {zkz.provider} {zkz.type} {zkz.name} "
                    if zkz.size:
                        mm += f"{zkz.size} "
                    if not zkz.color:
                        zkz.color = "-"
                        db.session.commit()
                    
                    if "media" in zkz.color:
                        viber.send_messages(OWNER_ID , [
                            PictureMessage(media = zkz.color , text = f"{zkz.name}")
                            ])
                        mm += f"Изображение №{i+1}. \n\n"
                    else:
                        mm += f"{zkz.color}. \n\n"
                    message += mm 
                message += f"{np.type} "
                if np.type == 'Наложеный платеж':
                    message += f"{np.oplata_nalojeniy}"
                    if np.doplata:
                        message += f"(вернуть {np.doplata})"
                    if np.back:
                        message += f"(доплатить {np.back})"
                if np.type == "ПриватБанк":
                    message += f"{np.oplata_card}"
                message += f" - {ttn}"
                viber.send_messages(OWNER_ID , [
                    TextMessage(None,None, message)
                    ])
                if np.region:
                    viber.send_messages(OWNER_ID , [
                        TextMessage(None,None, f"Коментарий: {np.region}")
                        ])
                back_to_menu(db,quer,viber) 
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id ).first()
                novap = NP.query.filter_by(user=usr).first()
                db.session.delete(novap)
                db.session.commit()
                return Response(status= 200)
            
            if quer.query_number == 'm17':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.oplata_nalojeniy  = viber_request.message.__getattribute__('text')
                quer.query_number = 'm18'
                db.session.commit()
                with open('./bot/buttons_conf/4menu_button.json') as f:
                    button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Должна ли я вам вернуть некую сумму денег, после получения наложенного платежа?'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status= 200)
            
            if quer.query_number == 'm18':
                if viber_request.message.__getattribute__('text') == 'Yes':
                    quer.query_number = 'm19'
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Напишите сумму, котрую я должна вам вернуть после получения наложенного платежа')
                        ])
                    return Response(status=200)
                if viber_request.message.__getattribute__('text') == 'No':
                    quer.query_number = 'm20'
                    with open('./bot/buttons_conf/4menu_button.json') as f:
                        button = json.load(f)
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None, 'Должны ли вы мне доплатить некую сумму денег к наложенному платежу?'),
                        KeyboardMessage(keyboard = button),
                        ])
                    return Response(status=200)

            if quer.query_number == 'm19':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.doplata  = viber_request.message.__getattribute__('text')
                quer.query_number = 'y1'  
                db.session.commit()
                with open('./bot/buttons_conf/6menu_button.json') as f:
                     button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Кто оплачивает услуги доставки'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status= 200)


            if quer.query_number == 'm20':
                if viber_request.message.__getattribute__('text') == 'No':
                    quer.query_number = 'y1'  
                    db.session.commit()
                    with open('./bot/buttons_conf/6menu_button.json') as f:
                         button = json.load(f)
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Кто оплачивает услуги доставки'),
                        KeyboardMessage(keyboard = button),
                        ])
                    return Response(status= 200)

                if viber_request.message.__getattribute__('text') == 'Yes':

                    quer.query_number = 'm21'  
                    db.session.commit()
                    viber.send_messages(viber_request.sender.id , [
                        TextMessage(None,None,'Напишите сумму, которую вы зачислите на карту'),
                        ])
                    return Response(status= 200)

            if quer.query_number == 'm21':
                usr = User.query.filter_by(user_viber_id=viber_request.sender.id).first()
                np = NP.query.filter_by(user=usr).first()
                np.back  = viber_request.message.__getattribute__('text')
                quer.query_number = 'y1'  
                db.session.commit()
                with open('./bot/buttons_conf/6menu_button.json') as f:
                     button = json.load(f)
                viber.send_messages(viber_request.sender.id , [
                    TextMessage(None,None,'Кто оплачивает услуги доставки'),
                    KeyboardMessage(keyboard = button),
                    ])
                return Response(status= 200)


        elif isinstance(viber_request, ViberConversationStartedRequest):
            try:
                user_viber_id=viber_request.__getattribute__('user').__getattribute__('id')
                nick = viber_request.__getattribute__('user').__getattribute__('name')
                new_User=User(user_viber_id=str(user_viber_id), nickname = str(nick))
                new_query = Query(query_number='m1',user = new_User, zakaz_num = 1)
                db.session.add(new_User)
                db.session.add(new_query)
                db.session.commit() 
            except:
                pass
            try:
                viber.send_messages(user_viber_id, [
                    TextMessage(None,None, 'Напишите любой текст для начала. Что бы все сбросить и начать сначала напишите /reset')
                    ])
            except:
                pass
            return Response(status=200)


        return Response(status=200)





    

