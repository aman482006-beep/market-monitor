from openai import AsyncOpenAI
from app.core.config import settings

async def explain_market(facts: dict) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": "You are a market commentary assistant. Use ONLY supplied backend facts. Never invent prices, flows, breadth, earnings, or statistics. Label interpretation as interpretation and keep the response concise."},
            {"role": "user", "content": f"Explain the market state from these backend facts only:\n{facts}"},
        ],
    )
    return response.output_text
