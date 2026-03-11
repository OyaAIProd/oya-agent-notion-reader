import os
import json
import uuid
import base64

inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
prompt = inp.get("prompt", "").strip()
if not prompt:
    print(json.dumps({"error": "No prompt provided"}))
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Generator definitions — each returns (model_label, file_path) on success
# ---------------------------------------------------------------------------

def generate_flux(prompt: str) -> tuple[str, str]:
    """FLUX.1 Schnell via HuggingFace Inference API — returns raw PNG bytes."""
    import httpx

    token = os.environ["HF_API_TOKEN"]
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt}

    resp = httpx.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()

    path = f"/tmp/flux_{uuid.uuid4().hex[:8]}.png"
    with open(path, "wb") as f:
        f.write(resp.content)
    return ("FLUX.1 Schnell", path)


def generate_nano_banana(prompt: str) -> tuple[str, str]:
    """Nano Banana 2 via Google GenAI SDK (Gemini 3.1 Flash Image Preview)."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            path = f"/tmp/nano_banana_{uuid.uuid4().hex[:8]}.png"
            with open(path, "wb") as f:
                f.write(part.inline_data.data)
            return ("Nano Banana 2", path)

    raise RuntimeError("No image data in Gemini response")


def generate_gpt_image(prompt: str) -> tuple[str, str]:
    """GPT Image 1 via OpenAI SDK — returns base64 PNG."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )

    b64 = result.data[0].b64_json
    img_bytes = base64.b64decode(b64)
    path = f"/tmp/gpt_image_{uuid.uuid4().hex[:8]}.png"
    with open(path, "wb") as f:
        f.write(img_bytes)
    return ("GPT Image 1", path)


# ---------------------------------------------------------------------------
# Pick first 2 available generators based on which env vars are set
# ---------------------------------------------------------------------------

GENERATORS = []
if os.environ.get("HF_API_TOKEN"):
    GENERATORS.append(generate_flux)
if os.environ.get("GOOGLE_API_KEY"):
    GENERATORS.append(generate_nano_banana)
if os.environ.get("OPENAI_API_KEY"):
    GENERATORS.append(generate_gpt_image)

if len(GENERATORS) < 2:
    print(json.dumps({
        "error": "At least 2 API keys required. Configure HF_API_TOKEN, GOOGLE_API_KEY, or OPENAI_API_KEY."
    }))
    raise SystemExit(1)

generators = GENERATORS[:2]

# ---------------------------------------------------------------------------
# Run the two generators
# ---------------------------------------------------------------------------

results = []
errors = []

for gen in generators:
    try:
        label, path = gen(prompt)
        print(f"A2ABASEAI_FILE: {path}")
        results.append({"model": label, "file": path})
    except Exception as e:
        errors.append({"generator": gen.__name__, "error": str(e)})

if not results:
    print(json.dumps({"error": "All generators failed", "details": errors}))
    raise SystemExit(1)

summary = {
    "ok": True,
    "prompt": prompt,
    "images": results,
}
if errors:
    summary["errors"] = errors

print(json.dumps(summary))
