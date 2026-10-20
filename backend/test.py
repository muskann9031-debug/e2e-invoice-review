"""One-request smoke check for the configured Azure OpenAI deployment."""

from app.providers.azure_openai import AzureOpenAIService


def main() -> None:
    service = AzureOpenAIService()
    answer = service.generate_text("What is the capital of France?")
    print(f"answer: {answer}")


if __name__ == "__main__":
    main()
