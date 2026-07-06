from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from .intents import INTENTS

MODEL_NAME = "Qwen/Qwen3-0.6B"

print("Loading SLM...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)
model.config.tie_word_embeddings = False
print("SLM ready!")

def classify_intent(text):
    """Classify user input into one of the defined intents.
    
    Args:
        text: User input string to classify
        
    Returns:
        str: Intent name or 'chat' if classification fails
    """
    # Final safety check
    if not text or not isinstance(text, str):
        return "chat"
    
    text = text.strip()
    if not text:
        return "chat"
    
    prompt = f"""You are an intent classifier for a desktop AI assistant.
                Classify the user's command into exactly one of these intents:
                {", ".join(INTENTS)}

                Rules:
                - Reply with ONLY the intent name, nothing else
                - No explanation, no punctuation, just the intent
                - If nothing matches, reply with: chat

                User command: "{text}"
                Intent:"""

    messages = [{"role": "user", "content": prompt}]

    try:
        input_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False       # disable chain of thought
        )

        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=5,       # intent is always 1-2 words
                do_sample=False,        # deterministic output
                temperature=None,
                top_p=None,
            )

        response = tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        ).strip().lower()

        print(f"SLM classified '{text}' → '{response}'")

        # validate — if model returns something unexpected fall back to chat
        return response if response in INTENTS else "chat"
    
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "chat"
