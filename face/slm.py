import logging
import threading

from .intents import INTENTS

logger = logging.getLogger(__name__)

MODEL_NAME = "Qwen/Qwen3-0.6B"

_model = None
_tokenizer = None
_model_lock = threading.Lock()
_inference_lock = threading.Lock()


class ChatGenerationError(RuntimeError):
    pass


def _get_model():
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        with _model_lock:
            if _model is None or _tokenizer is None:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer

                logger.info("Loading language model %s", MODEL_NAME)
                tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME,
                    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto",
                )
                model.config.tie_word_embeddings = False
                _tokenizer = tokenizer
                _model = model
                logger.info("Language model is ready")

    return _tokenizer, _model


def _generate(messages, max_new_tokens):
    import torch

    tokenizer, model = _get_model()
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with _inference_lock, torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    return tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True,
    ).strip()


def classify_intent(text):
    """Classify input into a known intent, falling back to chat on failure."""
    if not isinstance(text, str) or not text.strip():
        return "chat"

    prompt = f"""You are an intent classifier for a desktop AI assistant.
Classify the user's command into exactly one of these intents:
{", ".join(INTENTS)}

Reply with only the intent name. If nothing matches, reply with: chat

User command: {text.strip()}
Intent:"""

    try:
        response = _generate([{"role": "user", "content": prompt}], 5).lower()
        logger.debug("Intent classification completed: %s", response)
        return response if response in INTENTS else "chat"
    except Exception:
        logger.exception("Intent classification failed")
        return "chat"


def generate_reply(text):
    """Generate an assistant response or raise ChatGenerationError."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("A non-empty message is required")

    try:
        response = _generate(
            [{"role": "user", "content": text.strip()}],
            max_new_tokens=128,
        )
    except Exception as exc:
        logger.exception("Chat response generation failed")
        raise ChatGenerationError("The language model could not generate a response") from exc

    if not response:
        logger.error("Language model returned an empty chat response")
        raise ChatGenerationError("The language model returned an empty response")
    return response
