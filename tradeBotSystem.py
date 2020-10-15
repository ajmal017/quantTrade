import yahoodata
import logging
import logging.handlers
import numpy as np
import supertrend2 as supertrend
import cmd
import uuid
import matplotlib.pyplot as plt
import mplfinance as mpf
import excelTradeLogs

class Terminal(cmd.Cmd):

    intro = 'Welcome to kr0nos Trading System. Type help or ? to list commands.\n'
    prompt = 'kr0n0s => '
    tickers = ''
    period = ''
    startDate = ''
    endDate = ''
    stPeriod = 0
    stFactor = 0
    maxExposure = 0
    correlationId = ''
    performance = 0
    
    '''
    Business Logic Functions
    '''
    def runSuperTrend(self, df):
        dfSt = supertrend.ST(df=df, f=int(self.stFactor), n=int(self.stPeriod))
        return dfSt
    
    def plotGraph(self, df):
        apdict = mpf.make_addplot(df['SuperTrend'])
        mpf.plot(df, type='candle', addplot=apdict)

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
            self.sizePosition = int(input('Position Size: [R$ 10.000,00') or 10000)
            self.maxExposure = int(input('Max Exposure: [R$ 200.000,00') or 200000)
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
        logger.info('Running backtest emulation')
        self.backtest()
    
    def backtest(self):
        df = yahoodata.getData(tickers=self.tickers, startDate=self.startDate, endDate=self.endDate, interval=self.period)
        dfSuperTrendSignal = self.runSuperTrend(df)
        
        currentPosition = 0
        currentPrice = 0
        self.performance = 0

        for i in range(1, len(dfSuperTrendSignal) - 1):
            logger.debug('Evaluating data for Close: {} - SuperTrend: {} - Date: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i], dfSuperTrendSignal.index[i]))
            nextCandleOpen = dfSuperTrendSignal['Open'][i+1]
            
            if ((dfSuperTrendSignal['SuperTrend'][i] > 0) and (dfSuperTrendSignal['Signal'][i-1] == 'Sell') and (dfSuperTrendSignal['Signal'][i] == 'Buy')):
                logger.warning('Buy Setup activated Close: {} - SuperTrend: {} - Date: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i], dfSuperTrendSignal.index[i]))
                correlationId = uuid.uuid4().hex[:16]
                entryPrice = nextCandleOpen
                
                unitsBuy = int(self.maxExposure / entryPrice) + abs(currentPosition)
                
                if currentPosition != 0:
                    self.performance += abs(currentPosition * currentPrice) - (abs(currentPosition) * entryPrice)
                
                currentPosition += unitsBuy
                currentPrice = entryPrice
                
                if unitsBuy > 0:

                    dictIns = {
                        'CorrelationId': correlationId,
                        'Ticker': self.tickers,
                        'Units': unitsBuy,
                        'UnitValue': entryPrice,
                        'OrderType': 'Buy',
                        'Control': 'SuperTrend'
                    }

                    excelTradeLogs.writeExcel(dictIns)
                else:
                    logger.warning('Max Exposure reached! Stopping position trades.')
                
                continue

            elif ((dfSuperTrendSignal['SuperTrend'][i] > 0) and (dfSuperTrendSignal['Signal'][i-1] == 'Buy') and (dfSuperTrendSignal['Signal'][i] == 'Sell')):
                logger.warning('Sell Setup activated Close: {} - SuperTrend: {} - Date: {}'.format(dfSuperTrendSignal['Close'][i], dfSuperTrendSignal['SuperTrend'][i], dfSuperTrendSignal.index[i]))
                entryPrice = nextCandleOpen

                unitsSell = int(self.maxExposure / entryPrice) + currentPosition

                if currentPosition != 0:
                    self.performance += abs(currentPosition * entryPrice) - (abs(currentPosition) * currentPrice)

                currentPosition -= unitsSell
                currentPrice = entryPrice

                if unitsSell > 0:

                    dictIns = {
                        'CorrelationId': correlationId,
                        'Ticker': self.tickers,
                        'Units': unitsSell,
                        'UnitValue': entryPrice,
                        'OrderType': 'Sell',
                        'Control': 'SuperTrend'
                    }
                    excelTradeLogs.writeExcel(dictIns)
                else:
                    logger.warning('Max Exposure reached! Stopping position trades.')
                continue

        logger.warning('Performance until now: {}'.format(self.performance))
        logger.warning('Current Position: {}'.format(currentPosition))
        #self.plotGraph(dfSuperTrendSignal)

    def do_draft(self, line):
        logger.info('Running tests for best factor')
        bestPerformance = -1000000000
        bestFactor = 7
        for i in range(1, self.stFactor):
            self.stFactor = i
            self.backtest()
            if self.performance > bestPerformance and self.performance != 0:
                bestPerformance = self.performance
                bestFactor = i
            self.performance = 0
        print(bestPerformance)
        print(bestFactor)

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