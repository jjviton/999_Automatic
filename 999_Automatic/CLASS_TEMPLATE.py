# -*- coding: utf-8 -*-


"""
******************************************************************************
Clase que implementa una 
 
******************************************************************************
******************************************************************************

Mejoras:    

Started on DIC/2022
Version_1: 

Objetivo: 

Author: J3Viton

"""

# J3_DEBUG__ = False  #variable global (global J3_DEBUG__ )


################################ IMPORTAMOS MODULOS A UTILIZAR.
import pandas as pd
import numpy as np

import yfinance as yf


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
logging.warning('esto es una kkk')

#### Variables globales  (refereniarlas con 'global' desde el codigo
versionVersion = 1.1
globalVar  = True



pdf_flag =True
epochs_ =12

#################################################### Clase Estrategia 



class xxxClass:

    """CLASE xxx

       
    """  
    
    #Variable de CLASE
    backtesting = False  #variable de la clase, se accede con el nombre
    n_past = 14  # Number of past days we want to use to predict the future.  FILAS
    flag01 =0
   
    def __init__(self, previson_a_x_days=4, Y_supervised_ = 'hull', para1=False, para2=1):
        
        #Variable de INSTANCIA
        self.para_02 = para2   #variable de la isntancia
        

        
        
        globalVar = True
        LSTMClass.flag01 =True
        
        return
    
    """
    Getter y setter para el acceso a atributo/propiedades
    """    
    def __getattribute__(self, attr):
        if attr == 'loss':
            return self._loss
        elif attr == 'xxx':
            return self._edad
        else:
            return object.__getattribute__(self, attr)

    def __setattr__(self, attr, valor):
        if attr == 'loss':
            self._loss = valor
        elif attr == 'xxx':
            self._edad = valor
        else:
            object.__setattr__(self, attr, valor)    
    
        
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
        

    
    """   
    print(sys.argv[1])   #se configura en 'run' 'configuration per file'
    print ('version(J): ',versionVersion) 

    if (True or sys.argv[1]== 'prod' ):
        print('Produccion')
        sys.exit()
    
    from alpaca.trading.client import TradingClient
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.stream import TradingStream
    import config
    
    client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
    account = dict(client.get_account())
    for k,v in account.items():
        print(f"{k:30}{v}")
    
    order_details = MarketOrderRequest(
        symbol= "SPY",
        qty = 100,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.DAY
    )
    
    # order = client.submit_order(order_data= order_details)
    #
    # trades = TradingStream(config.API_KEY, config.SECRET_KEY, paper=True)
    # async def trade_status(data):
    #     print(data)
    #
    # trades.subscribe_trade_updates(trade_status)
    # trades.run()
    
    assets = [asset for asset in client.get_all_positions()]
    positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]
    print("Postions")
    print(f"{'Symbol':9}{'Qty':>4}{'Value':>15}")
    print("-" * 28)
    for position in positions:
        print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")
    
    client.close_all_positions(cancel_orders=True) 




   
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
    
