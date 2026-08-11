import pandas as pd
import numpy as np
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class BacktesterBase:
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        print(f"📥 Descargando datos históricos de {self.symbol}...")
        self.data = yf.download(self.symbol, start=start_date, end=end_date, progress=False)
        
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.droplevel(1)
            
        if self.data.empty:
            print("⚠️ ADVERTENCIA: No se pudieron descargar datos. Verifique su conexión.")
            
    def estrategia_cruce_medias(self, corta: int = 20, larga: int = 50) -> pd.DataFrame:
        if self.data.empty:
            return self.data
            
        print(f"⚙️ Probando estrategia: Cruce de Medias ({corta}/{larga})...")
        df = self.data.copy()
        df['Media_Corta'] = df['Close'].rolling(window=corta).mean()
        df['Media_Larga'] = df['Close'].rolling(window=larga).mean()
        df['Senal'] = np.where(df['Media_Corta'] > df['Media_Larga'], 1, 0)
        df['Posicion'] = df['Senal'].shift(1)
        df['Retorno_Mercado'] = df['Close'].pct_change()
        df['Retorno_Estrategia'] = df['Posicion'] * df['Retorno_Mercado']
        df['Retorno_Acumulado'] = (1 + df['Retorno_Estrategia']).cumprod()
        return df

    def generar_reporte(self, df: pd.DataFrame):
        if df.empty or df['Retorno_Acumulado'].dropna().empty:
            print("\n" + "="*45)
            print("❌ REPORTE FALLIDO: No hay datos suficientes para calcular el retorno.")
            print("="*45)
            return
            
        retorno = (df['Retorno_Acumulado'].dropna().iloc[-1] - 1) * 100
        print("\n" + "="*45)
        print(f"📊 REPORTE DE LABORATORIO: {self.symbol}")
        print(f"💰 Retorno Total Simulado: {retorno:.2f}%")
        print(f"📅 Días de datos procesados: {len(df.dropna())}")
        print("="*45)

if __name__ == "__main__":
    bot = BacktesterBase(symbol="AAPL", start_date="2023-01-01", end_date="2024-01-01")
    resultados = bot.estrategia_cruce_medias()
    bot.generar_reporte(resultados)
