---
name: image-generate
display_name: "Image Generation"
description: "Generate images from text prompts using top AI models (FLUX, Nano Banana 2, GPT Image)"
category: general
icon: image
skill_type: sandbox
catalog_type: addon
requirements: "google-genai>=1.0 openai>=1.0"
resource_requirements:
  - env_var: HF_API_TOKEN
    name: "HuggingFace Token"
    description: "Free HuggingFace access token for FLUX.1 Schnell"
  - env_var: GOOGLE_API_KEY
    name: "Google API Key"
    description: "Google API key for Nano Banana 2 (Gemini 3.1 Flash Image)"
  - env_var: OPENAI_API_KEY
    name: "OpenAI API Key"
    description: "OpenAI API key for GPT Image 1"
tool_schema:
  name: image_generate
  description: "Generate images from a text prompt. Always produces 2 images from different AI models for comparison."
  parameters:
    type: object
    properties:
      prompt:
        type: string
        description: "Text description of the image to generate"
    required: [prompt]
---
# Image Generation
Generate images from text prompts using top AI models (FLUX, Nano Banana 2, GPT Image). Always produces 2 images from different models for comparison.
