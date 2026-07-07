#!/data/data/com.termux/files/usr/bin/python3
"""
Script para descargar precios de BTC/USDT desde Binance
"""

import ccxt
import json
from datetime import datetime

def main():
    print("📡 Conectando a Binance...")
    
    # Crear instancia de Binance
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    try:
        # Obtener precios de BTC/USDT
        ticker = exchange.fetch_ticker('BTC/USDT')
        
        # Preparar datos
        datos = {
            "timestamp": datetime.now().isoformat(),
            "symbol": ticker['symbol'],
            "last": ticker['last'],
            "bid": ticker['bid'],
            "ask": ticker['ask'],
            "high": ticker['high'],
            "low": ticker['low'],
            "volume": ticker['baseVolume']
        }
        
        # Guardar en archivo JSON
        filename = f"btc_usdt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(datos, f, indent=2)
        
        print(f"✅ Datos guardados en: {filename}")
        print(f"💰 Precio actual de BTC: ${datos['last']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
