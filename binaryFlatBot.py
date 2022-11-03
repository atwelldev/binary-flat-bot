import websocket                                                                    
import json
import requests
import sqlite3
import time 
import datetime
import math
import ast
import colorama
import asyncio
import os

colorama.init()
# Name:     flatAnnunciator	
# key:      RJpjMGHozVCgTDJ 
# app_id:   23639	
# accuracy: 80%

# pip3 install websocket-client

# for check markets (active symbols)
# { 
#   "active_symbols": "brief",
#   "product_type": "basic"
# }

# for take price (ticks)
# {
#   "ticks":"frxAUDUSD"
# }
# ticks update: {"echo_req":{"time":1},"msg_type":"time","time":1600090928} echo_req - request msg_type - name of request

# for take candles history (ticks history) 
# {
#   "ticks_history": "R_50",
#   "adjust_start_time": 1,
#   "count": 10,
#   "end": "latest",
#   "start": 1,
#   "style": "candles"
# }

global lastTick
global currencysCheck
currencysCheck = {'frxAUDJPY': True, "frxEURAUD": True, "frxEURCHF": True, "frxEURJPY": True, "frxGBPAUD": True, "frxGBPUSD": True, "frxUSDCHF": True, "frxAUDUSD": True, "frxEURCAD": True, "frxEURGBP": True, "frxEURUSD": True, "frxGBPJPY": True, "frxUSDCAD": True, "frxUSDJPY": True}
global apiUrl
apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id=23639"
global rangeMult
global historySize
global allowedCandleValue
global mainCandlePass
global sleepDuration
global minDots
global maxDots


os.system('mode 28,37')

def wsOnOpen(ws, symbol):
    json_data = json.dumps({ "ticks": symbol })                     #dumps - transform  obj type to json str *see json commands in binary API * : [] - return some messages accordenly array members value
    ws.send(json_data)                                                                  #send a json to server

# def wsOnMessage(ws, message):
#     message = ast.literal_eval(message)
#     lastTick = message["tick"]["ask"]
#     symbol = message["tick"]["symbol"]

#     print(colorama.Fore.YELLOW + f'{message["tick"]["symbol"]}' + colorama.Fore.WHITE + f' {lastTick}')                       

#     if currencysCheck[symbol] and symbol == 'frxAUDUSD':
#         asyncio.create_task(checkSymbol(symbol, candleRecv(symbol)))
#     elif currencysCheck[symbol] and symbol == 'frxEURUSD':
#         asyncio.create_task(checkSymbol(symbol, candleRecv(symbol)))
#     elif currencysCheck[symbol] and symbol == 'frxEURJPY':
#         asyncio.create_task(checkSymbol(symbol, candleRecv(symbol)))def
    #checkSymbol(symbol, candleRecv(symbol))

    
def candleRecv(symbol):
    toSend = json.dumps({"ticks_history": f"{symbol}","adjust_start_time": 1,"count": historySize,"end": "latest","start": 1,"style": "candles"})
    cr = websocket.create_connection(apiUrl)
    cr.send(toSend)
    return cr.recv()

def sendFlat(symbol = None):
    time = datetime.datetime.today()
    requests.get(f'=Currency pair: {symbol}\nTime: {time}')

async def checkSymbol(symbol, candleHistory):
    candleArray = ast.literal_eval(candleHistory)["candles"]
    sameValueCount = 0
    candleAmong = 0
    high = candleArray[len(candleArray) - 2]['close'] + (candleArray[len(candleArray) - 2]['close'] / 100000 * rangeMult) #5
    low  = candleArray[len(candleArray) - 2]['close'] - (candleArray[len(candleArray) - 2]['close'] / 100000 * rangeMult)
 
    for n in candleArray:
        if (low <= n['close'] <= high or low <= n['open'] <= high) and candleArray[len(candleArray) - 1]['close'] > candleArray[len(candleArray) - 1]['open'] and candleArray[len(candleArray) - 2]['close'] < candleArray[len(candleArray) - 2]['open']:
            candleAmong += 1

    for i in candleArray:
        indexI = candleArray.index(i) 

        # debug
        # print(f"high: {high} low: {low}")
        # print(f"красная свеча {i['close'] < i['open']} {i['close']} {i['open']}")
        # print(f"зеленая свеча(сосед) {candleArray[indexI + 1]['close'] > candleArray[indexI + 1]['open']}")
        # print(colorama.Fore.RED + f"принадлежит диапозону: {low <= i['close'] <= high}" + colorama.Fore.WHITE)
        # print(colorama.Fore.RED + f"последний элемент зеленый: {candleArray[len(candleArray) - 1]['close'] > candleArray[len(candleArray) - 1]['open']} close: {candleArray[len(candleArray) - 1]['close']} open: {candleArray[len(candleArray) - 1]['open']}" + colorama.Fore.WHITE)
       
        if i['close'] < i['open'] and candleArray[indexI + 1]['close'] > candleArray[indexI + 1]['open'] and len(candleArray) - mainCandlePass != indexI: 
            #print(colorama.Fore.GREEN + 'первый этап пройден' + colorama.Fore.WHITE)
            if low <= i['close'] <= high and candleArray[len(candleArray) - 1]['close'] > candleArray[len(candleArray) - 1]['open'] and candleArray[len(candleArray) - 2]['close'] < candleArray[len(candleArray) - 2]['open']:
                sameValueCount += 1
        elif candleArray.index(i) == len(candleArray) - mainCandlePass:
            break 
        else:
            continue

    #print(candleAmong)
    #print(sameValueCount)
    if minDots <= sameValueCount <= maxDots and candleAmong <= allowedCandleValue:
        currencysCheck[symbol] = False
        print(colorama.Fore.LIGHTGREEN_EX + '\n FLAT DETECTED!\n' + colorama.Fore.LIGHTBLACK_EX + '\n----------------------------')
        sendFlat(symbol)
        await asyncio.sleep(sleepDuration)
        currencysCheck[symbol] = True
    
async def main():                         
    #ws = websocket.WebSocketApp(apiUrl, on_message = wsOnMessage, on_open = wsOnOpen)   #create websocket. on_open - starts when webscoekt is created, on_message starts when websocket taking a message from server (return message) 
    while True:
        for sym in currencysCheck:
            
            ws = websocket.create_connection(apiUrl)
            wsOnOpen(ws, sym)

            message = ast.literal_eval(ws.recv())
            lastTick = message["tick"]["ask"]
            symbol = message["tick"]["symbol"]

            candleHistory = candleRecv(symbol)

            print(colorama.Fore.LIGHTCYAN_EX + f' {datetime.date.today()} ' + colorama.Fore.WHITE + f'{str(datetime.datetime.now()).split()[1]}\n' + colorama.Fore.LIGHTYELLOW_EX + f' {message["tick"]["symbol"]}' + colorama.Fore.WHITE + f'  {lastTick}' + colorama.Fore.LIGHTRED_EX + f'\n Check ' + colorama.Fore.WHITE + f'     {currencysCheck[message["tick"]["symbol"]]}' + colorama.Fore.LIGHTBLACK_EX + '\n----------------------------')                       

            if currencysCheck[symbol]:
                asyncio.create_task(checkSymbol(symbol, candleHistory))
            
            await asyncio.sleep(0.5)

if __name__ == "__main__":   
    while True: 
        print(colorama.Fore.CYAN + '\n def' + colorama.Fore.WHITE + '    run default \n' + colorama.Fore.CYAN + ' set' + colorama.Fore.WHITE + '    run custom\n' + colorama.Fore.CYAN + ' help' + colorama.Fore.WHITE + '   commands' + colorama.Fore.CYAN + '\n info' + colorama.Fore.WHITE + '   about product')
        choice = input('\n ')
        print('')
        if choice == 'def':
            rangeMult           = 5
            historySize         = 60
            allowedCandleValue  = 11
            mainCandlePass      = 5
            sleepDuration       = 1200
            minDots             = 2
            maxDots             = 3
            break
        elif choice == 'set':
            rangeMult           = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' range multiply       ' + colorama.Fore.WHITE))
            historySize         = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' history size         ' + colorama.Fore.WHITE))
            allowedCandleValue  = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' allowed candle value ' + colorama.Fore.WHITE))
            mainCandlePass      = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' main candle pass     ' + colorama.Fore.WHITE))
            sleepDuration       = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' sleep duration       ' + colorama.Fore.WHITE))
            minDots             = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' min dots             ' + colorama.Fore.WHITE))
            maxDots             = int(input(colorama.Fore.LIGHTMAGENTA_EX + ' max dots             ' + colorama.Fore.WHITE))
            print('')
            break
        elif choice == 'def -s':
            print(colorama.Fore.LIGHTMAGENTA_EX + ' range multiply ' + colorama.Fore.WHITE + '      5')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' history size ' + colorama.Fore.WHITE + '        60')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' allowed candle value ' + colorama.Fore.WHITE + '11')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' main candle pass ' + colorama.Fore.WHITE + '    5')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' sleep duration ' + colorama.Fore.WHITE + '      1200')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' min dots ' + colorama.Fore.WHITE + '            2')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' max dots ' + colorama.Fore.WHITE + '            3')
        elif choice == 'info':
            print(colorama.Fore.LIGHTMAGENTA_EX + ' author' + colorama.Fore.WHITE + ' Denis Atwell\n' + colorama.Fore.LIGHTMAGENTA_EX + ' update' + colorama.Fore.WHITE + ' 09.30.2020\n')
            print("    Bot was created to help\n with flat detecting. He's \n looking for a flat in some  markets then send you a \n message.")
            print('    Accuracy depends on \n settings.')
            print(colorama.Fore.YELLOW + '\n all rights reserved ©' + colorama.Fore.WHITE)
        elif choice == 'help':
            #print(colorama.Fore.LIGHTMAGENTA_EX + '\n -def' + colorama.Fore.WHITE + '    use default \n' +  colorama.Fore.LIGHTMAGENTA_EX +' -def -s' + colorama.Fore.WHITE +' show default\n' + colorama.Fore.LIGHTMAGENTA_EX + ' -set' + colorama.Fore.WHITE + '    custom settings\n' + colorama.Fore.LIGHTMAGENTA_EX + ' -help' + colorama.Fore.WHITE + '   commands' + colorama.Fore.LIGHTMAGENTA_EX + '\n -info' + colorama.Fore.WHITE + '   about product')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' def' + colorama.Fore.WHITE + '    run default ')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' -s' + colorama.Fore.WHITE + '     show default ')
            print(colorama.Fore.LIGHTMAGENTA_EX + ' -c' + colorama.Fore.WHITE + '     change default ')
            print(colorama.Fore.LIGHTMAGENTA_EX + '\n set' + colorama.Fore.WHITE + '    run custom ')
            print(colorama.Fore.LIGHTMAGENTA_EX + '\n info' + colorama.Fore.WHITE + '   about product ')
            print(colorama.Fore.LIGHTMAGENTA_EX + '\n ^c' + colorama.Fore.WHITE + '     stop programm ')       
        else:
            print(colorama.Fore.RED + ' invalid value!' + colorama.Fore.WHITE)
    asyncio.run(main())
#     apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id=23639"                         #url for websocket (API URL)
#     ws = websocket.WebSocketApp(apiUrl, on_message = wsOnMessage, on_open = wsOnOpen)   #create websocket. on_open - starts when webscoekt is created, on_message starts when websocket taking a message from server (return message) 
#     ws.run_forever()
   
    
