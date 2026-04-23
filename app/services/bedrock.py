import os


class BedrockService:
    def __init__(self) -> None:
        self.region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
        )

    async def summarize(self, prompt: str) -> str:
        return (
            "Bedrock placeholder response. "
            f"region={self.region}, model_id={self.model_id}, prompt_length={len(prompt)}"
        )
