import yfinance as yf
import datetime
import logging
from workalendar.america import Brazil

def getHoliday(todayDate):
    brHolidays =  Brazil()

    if brHolidays.is_working_day(todayDate):
        return todayDate
    else:
        return -1
        
def getData(tickers, startDate, endDate, interval):
    data = yf.download(tickers=tickers, start=startDate, end=endDate, group_by="ticker", interval=interval)
    logging.info('Querying data for {} with {} - {} on interval {}'.format(tickers, startDate, endDate, interval))
    
    #if (getHoliday(startDate) == -1):
    #    logging.warning('Check paramete, Start Date is a holiday')
    
    return data