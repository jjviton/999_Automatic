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


Doc:
    https://alpaca.markets/sdks/python/

"""

# J3_DEBUG__ = False  #variable global (global J3_DEBUG__ )


################################ IMPORTAMOS MODULOS A UTILIZAR.
import pandas as pd
import numpy as np
import yfinance as yf

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, QueryOrderStatus
from alpaca.trading.requests import MarketOrderRequest,GetAssetsRequest,LimitOrderRequest,GetOrdersRequest
from alpaca.trading.stream import TradingStream

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.requests import StockLatestTradeRequest

from datetime import datetime

import config




import sys
sys.path.insert(0,"C:\\Users\\INNOVACION\\Documents\\J3\\100.- cursos\\Quant_udemy\\programas\\Projects\\libreria")

#Mis import
import quant_j3_lib as quant_j



####################### LOGGING

import logging    #https://docs.python.org/3/library/logging.html
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='C:\\Users\\INNOVACION\\Documents\\J3\\100.- cursos\\Quant_udemy\\programas\\Projects\\999_Automatic\\log\\registro_auto.log', 
                    level=logging.WARNING ,force=True,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logging.warning('esto es una pruba automatic.py')


#### Variables globales  (refereniarlas con 'global' desde el codigo para actualizar)
versionVersion = 0.1
globalVar  = True

file_path ="../../999_Automatic/reports/Cartera/cartera01.xlsx"
"""
name = 'cartera01'
file_path ="../reports/Cartera/"+name+".xlsx"
"""

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
        #file_path= "C:/Users/INNOVACION/Documents/J3/100.- cursos/Quant_udemy/programas/Projects/999_Automatic/reports/Cartera/" +name+ ".xlsx"
       
        if os.path.exists(file_path):
            print("CARTERA existe...")
        else:
            print("El archivo no existe.")
            self.crearCartera(name)   
        
        self.senalBeep()
        
        #activarlog()
        logging.warning('pasando por automatic.py')
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

        try:
            order = self.client.submit_order(order_data= order_details)     
        except:
            logging.error('Error en PlaceOrder BUY %s', instrument_)

    
        #order = self.client.submit_order(order_data= order_details)     
        
        
        self.senalBeep()

        return order.id
    
    def placeBracketOrder(self, instrument_ ='AAPL', quantity_=1, TP_=2, SL_=1):

        #Ponemos una orden
        TP_ = round(TP_, 2)  #no podemos tener mas de dos decimales
        SL_ = round(SL_, 2)
        
        order_details = MarketOrderRequest(
            symbol= instrument_,
            qty = quantity_,
            side = OrderSide.BUY,
            time_in_force = TimeInForce.GTC,
            order_class='bracket',
            take_profit=dict(
                limit_price=(TP_),
            ),
            stop_loss=dict(
                stop_price=(SL_),
            )
        )

        try:        
            orden = self.client.submit_order(
                order_data= order_details
                )
            
            
            
            
            print("Orden bracket (Stop Loss y Take Profit) realizada con éxito:")
            print(orden)
        except Exception as e:
            print("Error al realizar la orden bracket:")
            print(e)
            logging.error(e)   



        
        
    
    

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
        
        #En este caso no aplicamos aquí la estrategia, se calcula en la funion del backtesting
        if (not(TP > SL*1.5)):
            pass
            #return (-1* (TP/SL))  #-2 
        
        #☻ calculo numero de acciones
        quote,openMarket = self.getLastQuote(instrument_)
        cantidad = int (((cash * 0.1)/quote))
        
        if ((cash *0.015) < (SL*cantidad)):
            #return -3
            pass
        
        #if((TP*100/quote)<6):   # beneficio menor que el 6%
        #    return -4
        #esto lo controlo con el valor 'expectancy' del Backtesting
        
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

        #file_path ="../reports/Cartera/"+name+".xlsx"
        
        #hago una copia porsi
        import shutil

        shutil.copy2(file_path, "cartera_back.xlsx")

        self.cartera202301= pd.read_excel(file_path, index_col=0)
    
        return 

    def actualizarCartera(self, name, nuevaPosicion):
        """
        Creo un DF con las posisciones y lo guardo en un Excel.
        
        """
        self.leerCartera('cartera01')  
        self.cartera202301 = self.cartera202301._append(nuevaPosicion, ignore_index=True) #jjjjj

        #file_path ="../reports/Cartera/"+name+".xlsx"
        self.cartera202301.to_excel(file_path, 
             index=True,
             )

        
    
        return   
    
    def senalBeep(self):
        import winsound
        import time
        
        # Define la frecuencia y duración de los pitidos
        short_beep_freq = 1000 # Hz
        long_beep_freq = 2000 # Hz
        beep_duration = 100 # milisegundos
        
        # Genera la secuencia de pitidos
        winsound.Beep(short_beep_freq, beep_duration) # Pitido corto
        time.sleep(0.1) # Espera 0.1 segundos entre pitidos
        winsound.Beep(short_beep_freq, beep_duration) # Pitido corto
        time.sleep(0.2) # Espera 0.2 segundos entre pitidos
        winsound.Beep(long_beep_freq, beep_duration*3) # Pitido largo
                

    def get_transactions(self, start_date, end_date):
        # Convertir las fechas a objetos datetime
        """start_datetime = pd.Timestamp(start_date, tz='America/New_York')
        end_datetime = pd.Timestamp(end_date, tz='America/New_York')
        """
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        
        request_params = GetOrdersRequest(
                            after = start_datetime,
                            until = end_datetime,
                            status=QueryOrderStatus.ALL,
                            limit =500
            )
        
        # Obtener todas las órdenes en el rango de fechas
        orders = self.client.get_orders(filter = request_params)

        return orders
    
    def anotar_excel_v2(self, ordersData, nombre_archivo):         
        #datos guarda en cada iteracion del bucle los datos de cada transaccion
        datos = ordersData
        try:
            with pd.ExcelWriter(nombre_archivo) as writer:
                df = datos
                df.to_excel(writer, sheet_name='Operaciones', index=False)

            print(f"Datos escritos exitosamente en {nombre_archivo}")
        except Exception as e:
            print(f"Error al escribir en el archivo Excel: {e}")

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


    incluimos ademas una parte de codigo en el main que hace un informe de las operaciones realizadas en un rangp
    
    """   
    print(sys.argv[1])   #se configura en 'run' 'configuration per file'
    print ('version(J): ',versionVersion) 

    if (sys.argv[1]== 'prod' ):
        print('Produccion')
        sys.exit()
     
    
    #Llamamos al constructor de la Clase
    alpacaAPI= tradeAPIClass()        
     
    # bajar las transacciones
    # Define el rango de fechas
    start_date = '2020-01-01'
    end_date = '2024-09-4'
    # Llamada a la función
    transactions = alpacaAPI.get_transactions(start_date, end_date)
    
    #convertimos la list a data frame
    # Convertir la lista de órdenes a un DataFrame de pandas directamente
    #df_orders = pd.DataFrame([transactions._raw for order in transactions])
    
    # Convertir la lista de órdenes a una lista de diccionarios
    orders_data = []
    for order in transactions:
        orders_data.append({
            'id': order.id,
            'symbol': order.symbol,
            'qty': order.qty,
            'filled_qty': order.filled_qty,
            'type': order.type,
            'side': order.side,
            'status': order.status,
            'submitted_at': str(order.submitted_at),
            'filled_at': str(order.filled_at),
            'expired_at': str(order.expired_at),
            'canceled_at': str(order.canceled_at),
            'failed_at': str(order.failed_at),
            'replaced_at': str(order.replaced_at),
            'created_at': str(order.created_at),
            'updated_at': str(order.updated_at),
            'filled_avg_price': str(order.filled_avg_price)
        })

    # Crear un DataFrame de pandas
    df_orders = pd.DataFrame(orders_data)
    
    # Mostrar el DataFrame
    print(df_orders)
    #Imprimir datos en excel 
    file_path2 ="../docs/"+"analisis_estra_01"+".xlsx"
    alpacaAPI.anotar_excel_v2(df_orders, file_path2)

    # Imprime las transacciones obtenidas
    for transaction in transactions:
        print(transaction)



    sys.exit()    #me salgo para no ejecutar el resto del codigo.        


    
    alpacaAPI.senalBeep()

    #creamos la cartera
    #○alpacaAPI.crearCartera('cartera01')    
    #alpacaAPI.leerCartera('cartera01')   
    # Anadir una nueva fila al 
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
    

    
    # client = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
    # multi symbol request - single symbol is similar
    # multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY", "GLD", "TLT"])
    # latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)
    # gld_latest_ask_price = latest_multisymbol_quotes["GLD"].ask_price

    
    # 1.- Enviar Orden de compra BRAKET sl y tp incluidos
    
    alpacaAPI.placeBracketOrder( instrument_ ='AAPL', quantity_=1, TP_=210.30, SL_=210.0)

    """
    # 1. Enviar una orden de compra
    buy_order_data = LimitOrderRequest(
        symbol="AAPL",
        limit_price=200,  # Precio de compra deseado
        qty=10,  # Cantidad de acciones a comprar
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    
    buy_order = alpacaAPI.client.submit_order(order_data=buy_order_data)
    """
    

    
    
    
    
    
    # 2. Esperar a la ejecución de la orden de compra (puedes implementar lógica para monitorear el estado)
    
    # 3. Enviar una orden de venta limitada
    sell_order_data = LimitOrderRequest(
        symbol="INTC",
        limit_price=45,  # Precio de venta deseado
        qty=10,  # Cantidad de acciones a vender (igual a la cantidad comprada)
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
    
    sell_order = alpacaAPI.client.submit_order(order_data=sell_order_data)
    
    
    # attempt to cancel all open orders
    #cancel_statuses = client.cancel_orders()




    #POSITIONS
   
    #pos= client.get_all_positions()  
    
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
    