from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os


def main():
    ckpt_root = os.path.join("models", "crisis_classifier")
    checkpoints = [d for d in os.listdir(ckpt_root) if d.startswith("checkpoint-")]
    if not checkpoints:
        raise SystemExit("No checkpoints found in models/crisis_classifier")
    checkpoints.sort(key=lambda x: int(x.split("-")[1]))
    best = os.path.join(ckpt_root, checkpoints[-1])
    print("Extracting from:", best)

    model = AutoModelForSequenceClassification.from_pretrained(best)

    try:
        tokenizer = AutoTokenizer.from_pretrained(best)
    except Exception as e:
        print("Tokenizer load from checkpoint failed:", e)
        # fallback to repo-level tokenizer if present
        tokenizer = AutoTokenizer.from_pretrained(ckpt_root)

    model.save_pretrained(ckpt_root)
    tokenizer.save_pretrained(ckpt_root)
    print("Done")


if __name__ == "__main__":
    main()
