import yfinance as yf
import datetime
import calendar
import pandas as pd
from workalendar.america import Brazil
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib as mpl


def getTickersData(tickers, startDate, endDate, interval):
    data = yf.download(tickers=tickers, start=startDate, end=endDate, group_by="ticker", interval=interval)
    return data

def getExecutionDate():
    todayDate = datetime.datetime.today()
    #previousDate = todayDate - datetime.timedelta(days=1)

    #while ((getHoliday(previousDate) == -1) and calendar.weekday(previousDate.year, previousDate.month, previousDate.day) in (5,6)):
    #    previousDate = todayDate - datetime.timedelta(days=1)

    #return previousDate
    return todayDate

def getHoliday(todayDate):
    brHolidays =  Brazil()

    if brHolidays.is_working_day(todayDate):
        return todayDate
    else:
        return -1

def getStartDate(executionDate):
    return executionDate - datetime.timedelta(days=90)

def volumeDistortions(data):
    #loop pelos tickers
    #print(data)
    for ticker, i in data:
        if i == 'Volume':
            todayVar = (((data[ticker]['Adj Close'][-1:][0]) - (data[ticker]['Open'][-1:][0])) / (data[ticker]['Adj Close'][-1:][0])) * 100
            todayVolume = data[ticker][i][-1:]
            last5Volume = data[ticker][i][-5:-1]
            last21Volume = data[ticker][i][-21:-1]
            last50Volume = data[ticker][i][-50:-1]
            
            if ((todayVolume[0] / last5Volume.mean()) > 1.4):
                print(ticker + ': ' + 'com volume 40% acima da média de 5 dias, fechando a ' + '{:.2f}% de oscilação no intra'.format(todayVar))
                #print(data[ticker]['Open'][-1:][0])
                #print(data[ticker]['Adj Close'][-1:][0])
            if ((todayVolume[0] / last21Volume.mean()) > 1.4):
                print(ticker + ': ' + 'com volume 40% acima da média de 21 dias, fechando a ' + '{:.2f}% de oscilação no intra'.format(todayVar))
            if ((todayVolume[0] / last50Volume.mean()) > 1.4):
                print(ticker + ': ' + 'com volume 40% acima da média de 50 dias, fechando a ' + '{:.2f}% de oscilação no intra'.format(todayVar))
            
if __name__ == '__main__':
    #Verificando se é dia útil para a execução
    executionDate = getExecutionDate()

    if executionDate != -1:
        print('Iniciando execução com referência: ' + str(executionDate))
        startDate = getStartDate(executionDate)

        #Formatando data de inicio para envio ao Yahoo Finance
        startDateFmt = str(startDate.year) + '-' + str(startDate.month) + '-' + str(startDate.day)
        endDateFmt = str(executionDate.year) + '-' + str(executionDate.month) + '-' + str(executionDate.day)

        #Alocando Tickers que serão utilizados
        tickers = 'PETR4.SA VALE3.SA ITUB4.SA IRBR3.SA JSLG3.SA MOVI3.SA BBAS3.SA BBDC4.SA CMIG4.SA FLRY3.SA MGLU3.SA VVAR3.SA ABEV3.SA AZUL4.SA B3SA3.SA BPAC11.SA CIEL3.SA ELET3.SA JBSS3.SA MRFG3.SA'
        #tickers = 'FLRY3.SA VALE3.SA'
        tickersData = getTickersData(tickers=tickers, startDate=startDateFmt, endDate='2020-07-03', interval='1d')

        volumeDistortions(tickersData)
        #writeExcel(filename=excelFilename, dictInsData=dictData, sheet='YahooFX', date=dateToday)
    else:
        print('Dia não útil!')