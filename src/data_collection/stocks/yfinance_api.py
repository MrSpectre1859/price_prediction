import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from zoneinfo import ZoneInfo
from src.config.constants import TICKERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_stock_data(
	ticker : str,
	days: int = 7,
	interval : str = "15m",
	save_raw: bool = True
	) -> pd.DataFrame:

	"""
	Baixa dados históricos de um ativo.

    Args:
        ticker (str): Código do ativo (ex: 'PETR4')
        days (int): Número de dias para coletar
        interval (str): Intervalo entre dados ('15m', '1h', etc)
        save_raw (bool): Se True, salva dados em data/raw/

    Returns:
        pd.DataFrame: Dados do ativo com colunas ['datetime', 'close']
	"""

	if interval not in ["15m", "1h", "1d"]:
		raise ValueError("Intervalo deve ser '15m', '1h' ou '1d'")

	try:
		yf_ticker = f"{ticker}.SA"
		tz_br = ZoneInfo("America/Sao_Paulo")

		start_date = datetime.now() - timedelta(days=days)
		end_date = datetime.now(tz_br)

		logger.info(f"Coletando {ticker} ({interval}) de {start_date.date} até {end_date.date}")

		data = yf.download(
			tickers = yf_ticker,
			start = start_date,
			end = end_date,
			interval = interval,
			progress = False
		)

		if data.empty:
			raise ValueError(f"Nenhum dado encontrado para {ticker} no período especificado")

		data = data[["Close"]].reset_index()
		data.columns = ["datetime", "close"]
		data["datetime"] = data["datetime"].dt.tz_convert(tz_br)

		if save_raw:
			raw_path = Path("data/raw/stocks/")
			raw_path.mkdir(parents=True, exist_ok=True)

			filename = f"{ticker}_{interval}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
			data.to_csv(raw_path / filename, index=False)
			logger.info(f"Dados salvos na pasta {raw_path/filename}")

		return data

	except Exception as e:
		logger.error(f"Exceção: {str(e)}")
		raise

if __name__ == "__main__":
	petr_data = get_stock_data(ticker = "PETR4", days = 5, interval = "15m")
	print(petr_data.head())