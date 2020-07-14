import yfinance as yf
import datetime
import calendar
import pandas as pd
from workalendar.america import Brazil


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