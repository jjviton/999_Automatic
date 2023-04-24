# -*- coding: utf-8 -*-


"""
******************************************************************************
Clase que implementa la conexion automatica al broker ALpaca

******************************************************************************
******************************************************************************

Mejoras:    

Started on Abril/2023
Version_1: 

Objetivo: 

Author: J3Viton

"""

# J3_DEBUG__ = False  #variable global (global J3_DEBUG__ )


################################ IMPORTAMOS MODULOS A UTILIZAR.
import pandas as pd
import numpy as np
import yfinance as yf

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce,AssetClass
from alpaca.trading.requests import MarketOrderRequest,GetAssetsRequest,LimitOrderRequest
from alpaca.trading.stream import TradingStream

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.requests import StockLatestTradeRequest

import config


import sys
sys.path.insert(0,"C:\\Users\\INNOVACION\\Documents\\J3\\100.- cursos\\Quant_udemy\\programas\\Projects\\libreria")

#Mis import
import quant_j3_lib as quant_j



####################### LOGGING
import logging    #https://docs.python.org/3/library/logging.html
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='../log/registro.log', level=logging.INFO ,force=True,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logging.warning('esto es una prueba')

#### Variables globales  (refereniarlas con 'global' desde el codigo para actualizar)
versionVersion = 0.1
globalVar  = True



pdf_flag =True
epochs_ =12

#################################################### Clase Estrategia 



class tradeAPIClass:

    """CLASE para comunicarme con el broker Online y colocar ordenes.
    
       
    """  
    
    #Variable de CLASE
    backtesting = False  #variable de la clase, se accede con el nombre
    n_past = 14  # Number of past days we want to use to predict the future.  FILAS
    flag01 =0
   
    def __init__(self, previson_a_x_days=4, Y_supervised_ = 'hull', para1=False, para2=1):
        
        #Variable de INSTANCIA
        self.para_02 = para2   #variable de la instancia
        globalVar = True
        tradeAPIClass.flag01 =True
        
        #Imprimimos la info de la cuenta
        self.client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
        account = dict(self.client.get_account())
        for k,v in account.items():
            print(f"{k:30}{v}")
            
        self.dataLog = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)  
        self.cartera202301=pd.DataFrame()
        
        #creamos la cartera si no existe
        import os
        name = 'cartera01'
        file_path ="../reports/Cartera/"+name+".xlsx"
       
        if os.path.exists(file_path):
            print("CARTERA existe.")
        else:
            print("El archivo no existe.")
            self.crearCartera(name)   
        
        return
  
    def getLastQuote(self, instrumento_="GLD"):
        """
        Descripcion: Funcion para saber el utlimo valor de un instrumento
        Devuelve estado del mercado open/close y ultima cotizacion
        
        -------
        """
        #jj cambiar quotes por trades       
        # multi symbol request - single symbol is similar
        multisymbol_request_params = StockLatestTradeRequest(symbol_or_symbols=[instrumento_, "GLD"])
        latest_multisymbol_trades = self.dataLog.get_stock_latest_trade(multisymbol_request_params)        
        latest_ask_price = latest_multisymbol_trades[instrumento_].price
                
        # Obtener el estado del reloj de Alpaca
        clock = self.client.get_clock()
           
        return latest_ask_price, clock.is_open
 
    def getCash(self):
        """
        Descripcion: Funcion para saber el dinero disponible en la cuenta

        """
        datosAccount= self.client.get_account()

        return float(datosAccount.cash)  #, datosAccount.equity, datosAccount.currency
       
    def placeOrder(self, instrument_='AAPL', quantity_=1):
        """
        Descripcion: Funcion para saber el dinero disponible en la cuenta

        """
        #Ponemos una orden
        order_details = MarketOrderRequest(
            symbol= instrument_,
            qty = quantity_,
            side = OrderSide.BUY,
            time_in_force = TimeInForce.DAY
        )
    
        order = self.client.submit_order(order_data= order_details)     
        
        # Añadir una nueva fila al 
        nueva_fila = {'nombre': 'Ana', 'edad': 28}
        df = df.append(nueva_fila, ignore_index=True)

        return order.id

    def getOrderStatus(self, orderID):
        """
        Descripcion: devuelve el estado de la orden
        return:
            NEW = <OrderStatus.NEW: 'new'>
            PARTIALLY_FILLED = <OrderStatus.PARTIALLY_FILLED: 'partially_filled'>
            FILLED = <OrderStatus.FILLED: 'filled'>
            DONE_FOR_DAY = <OrderStatus.DONE_FOR_DAY: 'done_for_day'>
            CANCELED = <OrderStatus.CANCELED: 'canceled'>
            EXPIRED = <OrderStatus.EXPIRED: 'expired'>
            REPLACED = <OrderStatus.REPLACED: 'replaced'>
            PENDING_CANCEL = <OrderStatus.PENDING_CANCEL: 'pending_cancel'>
            PENDING_REPLACE = <OrderStatus.PENDING_REPLACE: 'pending_replace'>
            PENDING_REVIEW = <OrderStatus.PENDING_REVIEW: 'pending_review'>
            ACCEPTED = <OrderStatus.ACCEPTED: 'accepted'>
            PENDING_NEW = <OrderStatus.PENDING_NEW: 'pending_new'>
            ACCEPTED_FOR_BIDDING = <OrderStatus.ACCEPTED_FOR_BIDDING: 'accepted_for_bidding'>
            STOPPED = <OrderStatus.STOPPED: 'stopped'>
            REJECTED = <OrderStatus.REJECTED: 'rejected'>
            SUSPENDED = <OrderStatus.SUSPENDED: 'suspended'>
            CALCULATED = <OrderStatus.CALCULATED: 'calculated'>
            HELD = <OrderStatus.HELD: 'held'>

        """
        order=self.client.get_order_by_id(orderID)   

        return order.status

    def positionExist(self, instrument_):
        #comprobar si tengo una posicion con un instumento
        try:
            position= self.client.get_open_position(instrument_)            
        except:
            return (0)
        return int(position.qty)


    def moneyManag(self,instrument_, TP, SL):
        """
        Descripcion: funcion que aniza las acciones condidatas y con reglas
        de moneyManagement decide cuantas comprar
        
        Si estoy dentro no comprar
        Espectativa de ganar doble de la de perder
        invertir un 10% de la cuenta /cash
                
        Returns
        -------
        -1 si no tenemos uqe comprar por los motivos X
        'cantidad' de acciones a comprar
        """
        
        #Si estoy dentro no entro más
        cantidad = self.positionExist(instrument_)    
        if (cantidad):
            return -1
        
        cash=  self.getCash()
        
        ## CONDICIONES PARA ENTRAR
        if (TP *1.0 < SL):
            pass
            #return -2
        
        #☻ calculo numero de acciones
        quote,openMarket = self.getLastQuote(instrument_)
        cantidad = int (((cash * 0.1)/quote))
        
        if ((cash *0.015) < (SL*cantidad)):
            return -3
        
        return cantidad
    
    
    def crearCartera(self, name):
        """
        Creo un DF con las posisciones y lo guardo en un Excel.
        
        """
        columnas = ['asset', 'qty','buyPrice','buyDay', 'SL', 'TP', 'sellDay', 'sellPrice', 'reason']
        df5 = pd.DataFrame(columns=columnas)
        file_path ="../reports/Cartera/"+name+".xlsx"
        df5.to_excel(file_path, 
             index=True,
             )
   
        return
    
    def leerCartera(self, name):
        """
       LLeo los datos de la cartera que tengo creada
        
        """

        file_path ="../reports/Cartera/"+name+".xlsx"
        
        #hago una copia porsi
        import shutil

        shutil.copy2(file_path, "../reports/Cartera/cartera_back.xlsx")

        self.cartera202301= pd.read_excel(file_path, index_col=0)
    
        return self.cartera202301

    def actualizarCartera(self, name, nuevaPosicion):
        """
        Creo un DF con las posisciones y lo guardo en un Excel.
        
        """
        self.leerCartera('cartera01')  
        self.cartera202301 = alpacaAPI.cartera202301.append(nuevaPosicion, ignore_index=True)

        file_path ="../reports/Cartera/"+name+".xlsx"
        self.cartera202301.to_excel(file_path, 
             index=True,
             )

        
    
        return   
        

        
    def analisis(self, instrumento, startDate, endDate, DF):
        """
        Descripcion: sample method
        
        Parameters
        ----------
        beneficio : TYPE
            DESCRIPTION.

        Returns
        -------


        """
        pass
   
        return
    
 
    
#################################################### Clase FIN






#/******************************** FUNCION PRINCIPAL main() *********/
#     def main():   
if __name__ == '__main__':    
        
    """Esta parte del codigo se ejecuta cuando llamo tipo EXE
    Abajo tenemos el else: librería que es cuando se ejecuta como libreria.
   
    Documentaicon del API     
    https://alpaca.markets/docs/trading/paper-trading/
    https://alpaca.markets/docs/python-sdk/api_reference/trading/requests.html

    
    """   
    print(sys.argv[1])   #se configura en 'run' 'configuration per file'
    print ('version(J): ',versionVersion) 

    if (sys.argv[1]== 'prod' ):
        print('Produccion')
        sys.exit()
        

    
    #Llamamos al constructor de la Clase
    alpacaAPI= tradeAPIClass()

    #creamos la cartera
    #○alpacaAPI.crearCartera('cartera01')    
    #alpacaAPI.leerCartera('cartera01')   
    # Añadir una nueva fila al 
    nuevaPosicion ={'asset':33, 'qty':2,'buyPrice':2,'buyDay':33, 'SL':4, 'TP':6, 'sellDay':4444, 'sellPrice':55, 'reason':'tp'}
    #alpacaAPI.cartera202301 = alpacaAPI.cartera202301.append(nuevaPosicion, ignore_index=True)
    alpacaAPI.actualizarCartera('cartera01', nuevaPosicion)


    #Obtener el dinero disponible
    cash=alpacaAPI.getCash() 
    
    #comprobar si tengo una posicion con un instumento

    #position= alpacaAPI.client.get_open_position('SAN')
    #print(position.qty)

    cantidad = alpacaAPI.positionExist('san')    
    

    #Obtener precio actual
    quote, marketOpen = alpacaAPI.getLastQuote("NXPI")

    #Poner una orden
    #orderID= alpacaAPI.placeOrder(instrument_='NXPI', quantity_=1)

    #Chequear estado de la orden  
    #status= alpacaAPI.getOrderStatus(orderID)

 
    #latest_trade = get_stock_latest_trade('AAPL')


    
    # Imprimir la información del último intercambio
    #print(latest_trade)


    # Voy a probar un funcion que recibe: instrumento, tp y SL
    # devolverá go_noGo, numero de acciones 
    TP = 10
    SL = 3
    instrumento_ = 'ENPH'
    
    numAcciones= alpacaAPI.moneyManag(instrumento_, TP, SL)
    



    # search for crypto assets
    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO)
    assets = alpacaAPI.client.get_all_assets(search_params)  
    #print(assets)
    

    #Concer datos de la cuenta
    datosAccount= alpacaAPI.client.get_account()
    print(str(datosAccount.equity), datosAccount.currency)
    print(datosAccount)
    
    #POSITIONS
    posotions= alpacaAPI.client.get_all_positions()  
    orders= alpacaAPI.client.get_orders()  
    
    datos= alpacaAPI.client.get_asset("AAPL")
    datos.tradable

    
    #Cotizaciones
    

    
    client = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
    # multi symbol request - single symbol is similar
    multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY", "GLD", "TLT"])
    
    latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)
    gld_latest_ask_price = latest_multisymbol_quotes["GLD"].ask_price


    
    
    limit_order_data = LimitOrderRequest(
                    symbol="BTC/USD",
                    limit_price=17000,
                    notional=4000,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.FOK
                   )

    """# Limit order
    limit_order = client.submit_order(
                order_data=limit_order_data
              )
    """
    
    # attempt to cancel all open orders
    #cancel_statuses = client.cancel_orders()




    #POSITIONS
   
    pos= client.get_all_positions()  
    
    #client.close_all_positions(cancel_orders=True)


    

    #STREAMING

    trading_stream = TradingStream('api-key', 'secret-key', paper=True)
    
    async def update_handler(data):
        # trade updates will arrive in our async handler
        print(data)
    
    # subscribe to trade updates and supply the handler as a parameter
    trading_stream.subscribe_trade_updates(update_handler)
    
    # start our websocket streaming
    #trading_stream.run() 
        
        
    
    
    """
    trades = TradingStream(config.API_KEY, config.SECRET_KEY, paper=True)
    async def trade_status(data):
        print(data)
    """    
    """
    
    trades.subscribe_trade_updates(trade_status)
    trades.run()
    """
    
    
    """
    assets = [asset for asset in client.get_all_positions()]
    positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]
    print("Postions")
    print(f"{'Symbol':9}{'Qty':>4}{'Value':>15}")
    print("-" * 28)
    for position in positions:
        print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")
    
    """
    # Close positions
    """
    #client.close_all_positions(cancel_orders=True) 
    """



   
    print('This is it................ 6')
    



else:    
    """
    Entrada por la librería.
    """
    """
    Esta parte del codigo se ejecuta si uso como libreria/paquete""    
    """    
    print (' libreria')
    print ('version(l): ',versionVersion)    
    
