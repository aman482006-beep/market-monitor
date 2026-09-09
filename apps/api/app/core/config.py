from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://market:market@localhost:5432/market_monitor"
    redis_url: str = "redis://localhost:6379/0"
    api_cors_origins: str = "http://localhost:3000"
    bharatstock_api_key: str = ""
    twelvedata_api_key: str = ""
    newsapi_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    kite_api_key: str = ""
    kite_api_secret: str = ""
    kite_redirect_url: str = "http://localhost:8000/api/broker/kite/callback"
    kite_access_token: str = ""
    default_universe: str = "NSE"
    global_symbols: str = "SPX,QQQ,NIKKEI,HSI,USD/INR,WTI/CRUDE,GOLD"
    news_query: str = "India stocks OR Nifty OR Sensex OR NSE OR BSE"
    kite_symbols: str = "NSE:NIFTY 50,NSE:RELIANCE,NSE:HDFCBANK,NSE:INFY"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
