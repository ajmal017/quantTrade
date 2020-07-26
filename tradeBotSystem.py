import yahoodata
import logging
import logging.handlers
import numpy as np
import supertrend
import cmd
import uuid
import excelTradeLogs

class Terminal(cmd.Cmd):

    intro = 'Welcome to kr0nos Algo Trading.   Type help or ? to list commands.\n'
    prompt = 'kr0n0sAlgoTrader => '
    tickers = ''
    period = ''
    startDate = ''
    endDate = ''
    stPeriod = 0
    stFactor = 0
    maxExposure = 100000
    correlationId = ''
    
    '''
    Business Logic Functions
    '''
    def runSuperTrend(self, df):
        dfSt = supertrend.ST(df=df, f=int(self.stFactor), n=int(self.stPeriod))
        return dfSt

    '''
    Command Control Functions
    '''
    def do_help(self, line):
        print('Documented commands:\n')
        print("\tconfig backtest -> let's try first")
        print("\tconfig run -> let's make this happen")
        print("\tbacktest -> play for now")
        print('\trun  -> power up')
        print("\tsummary -> let's  see waht we made")
        print('\texit -> see you soon')
        
    def do_exit(self, line):
        logger.info('Gain gain gain')
        return True
    
    def do_config(self, line):
        if line == 'backtest':
            logger.info('Configuring backtest mode')
            self.tickers = str(input('Tickers [VALE3.SA]: ') or 'VALE3.SA')
            self.period =  str(input('Period [60m]: ') or '60m')
            self.startDate = str(input('Start Date [2020-07-10]: ') or '2020-07-10')
            self.endDate = str(input('End Date [2020-07-17]: ') or '2020-07-17')
            self.stPeriod = int(input('SuperTrend Period [7]: ') or 7)
            self.stFactor = int(input('SuperTrend Factor [3]: ') or 3)
        elif line == 'run':
            logger.info('Configuring production mode')
            self.tickers = str(input('Tickers [VALE3.SA]: ') or 'VALE3.SA')
            self.period =  str(input('Period [60m]: ') or '60m')
            self.stPeriod = int(input('SuperTrend Period [7]: ') or 7)
            self.stFactor = int(input('SuperTrend Factor [3]: ') or 3)
            if 'm' in self.period:
                logger.info('Setting up for minutes period')
                #self.startDate = 
                #self.endDate =
            elif 'd' in self.period:
                logger.info('Setting up for days period')
                #self.startDate = 
                #self.endDate =
            else:
                logger.error('Period not recognized: {}'.format(self.period))
                return True
        else:
            logger.error('You should specify backtest or run')
            return True

    def do_backtest(self, line):
        logger.info('Running backtest mode')
        df = yahoodata.getData(tickers=self.tickers, startDate=self.startDate, endDate=self.endDate, interval=self.period)
        dfSuperTrendSignal = self.runSuperTrend(df)
        logger.info('SuperTrend Calculated')
        print(dfSuperTrendSignal)
        
        entryPrice = 0
        exitPrice = 0
        for i in range(1, len(dfSuperTrendSignal)):
            logger.debug('Evaluating data for Close: {} - SuperTrend: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i]))
            closePrice = dfSuperTrendSignal['Close'][i]
            if ((dfSuperTrendSignal['SuperTrend'][i] > 0) and (dfSuperTrendSignal['Signal'][i-1] == 'Sell') and (dfSuperTrendSignal['Signal'][i] == 'Buy')):
                logger.warning('Buy Setup activated Close: {} - SuperTrend: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i]))
                correlationId = uuid.uuid4().hex[:16]
                entryPrice = closePrice
                dictIns = {
                    'CorrelationId': correlationId,
                    'Ticker': self.tickers,
                    'Units': 100,
                    'UnitValue': entryPrice,
                    'OrderType': 'Buy',
                    'Control': 'SuperTrend'
                }
                excelTradeLogs.writeExcel(dictIns)
                continue
            elif ((dfSuperTrendSignal['SuperTrend'][i] > 0) and (dfSuperTrendSignal['Signal'][i-1] == 'Buy') and (dfSuperTrendSignal['Signal'][i] == 'Sell')):
                logger.warning('Sell Setup activated Close: {} - SuperTrend: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i]))
                if entryPrice > 0:
                    logger.warning('Selling positions')
                    exitPrice = closePrice
                    dictIns = {
                        'CorrelationId': correlationId,
                        'Ticker': self.tickers,
                        'Units': 100,
                        'UnitValue': exitPrice,
                        'OrderType': 'Sell',
                        'Control': 'SuperTrend'
                    }
                    excelTradeLogs.writeExcel(dictIns)
                    entryPrice = 0
                    exitPrice = 0
                continue
            elif (entryPrice > 0):
                logger.debug('Evaluating stop gain EntryPrice: {} - ClosePrice: {}'.format(entryPrice, closePrice))
                if ((closePrice > entryPrice) and (((closePrice - entryPrice)/entryPrice) > 0.04)):
                    logger.warning('Stop gain activated')
                    exitPrice = closePrice
                    dictIns = {
                        'CorrelationId': correlationId,
                        'Ticker': self.tickers,
                        'Units': 100,
                        'UnitValue': exitPrice,
                        'OrderType': 'Sell',
                        'Control': 'Stop Gain'
                    }
                    excelTradeLogs.writeExcel(dictIns)
                    entryPrice = 0
                    exitPrice = 0
                    continue
                logger.debug('Evaluating stop loss EntryPrice: {} - ClosePrice: {}'.format(entryPrice, closePrice))
                if ((closePrice < entryPrice) and ((abs(closePrice - entryPrice)/entryPrice) > 0.02)):
                    logger.warning('Stop loss activated')
                    exitPrice = closePrice
                    dictIns = {
                        'CorrelationId': correlationId,
                        'Ticker': self.tickers,
                        'Units': 100,
                        'UnitValue': exitPrice,
                        'OrderType': 'Sell',
                        'Control': 'Stop Loss'
                    }
                    excelTradeLogs.writeExcel(dictIns)
                    entryPrice = 0
                    exitPrice = 0
                    continue

    def do_run(self, line):
        return True

        
if __name__ == '__main__':
    logFileName = 'tradeBotSystem.log'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler(logFileName, when="D", interval=1, backupCount=30)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info('Trading System started')
    Terminal().cmdloop()