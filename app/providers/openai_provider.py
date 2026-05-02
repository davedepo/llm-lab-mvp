import os

from openai import OpenAI


def run_openai_experiment(
    prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    raise RuntimeError("OpenAI returned a response without output text.")
