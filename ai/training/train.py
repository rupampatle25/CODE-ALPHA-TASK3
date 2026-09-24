import os
import time
import json
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np

from ai.models.lstm_composer import LSTMComposer
from ai.preprocessing.sequence_encoder import MusicSequenceEncoder

BASE_AI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_AI_DIR, "data", "processed")
CHECKPOINTS_DIR = os.path.join(BASE_AI_DIR, "checkpoints")

def train_model(
    epochs: int = 40,
    batch_size: int = 32,
    learning_rate: float = 0.003,
    embedding_dim: int = 128,
    hidden_dim: int = 256,
    num_layers: int = 2,
    device_name: str = "cpu",
):
    """
    Trains the LSTMComposer model on processed musical token sequences.
    Saves model checkpoint to ai/checkpoints/melodia_lstm_v1.pt.
    """
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)

    # 1. Check data availability
    x_path = os.path.join(PROCESSED_DIR, "X.npy")
    y_path = os.path.join(PROCESSED_DIR, "y.npy")
    vocab_path = os.path.join(CHECKPOINTS_DIR, "vocab.json")

    if not (os.path.exists(x_path) and os.path.exists(y_path) and os.path.exists(vocab_path)):
        raise FileNotFoundError("Processed dataset files missing. Please run preprocessing first.")

    # 2. Load dataset and vocabulary
    encoder = MusicSequenceEncoder()
    encoder.load_vocab(vocab_path)
    vocab_size = encoder.vocab_size

    X_data = np.load(x_path)
    y_data = np.load(y_path)

    device = torch.device(device_name if torch.cuda.is_available() and device_name == "cuda" else "cpu")
    print(f"Training on device: {device} | Dataset size: {len(X_data)} samples | Vocab size: {vocab_size}")

    # 3. Create PyTorch DataLoader
    X_tensor = torch.tensor(X_data, dtype=torch.long)
    y_tensor = torch.tensor(y_data, dtype=torch.long)
    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 4. Initialize model
    model = LSTMComposer(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        dropout=0.2,
    ).to(device)

    criterion = nn.CrossEntropyLoss(ignore_index=0) # ignore PAD token
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)

    print("\n--- Starting LSTM Training ---")
    start_time = time.time()
    best_loss = float("inf")
    history = []

    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        num_batches = 0

        for batch_x, batch_y in dataloader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            optimizer.zero_grad()
            logits, _ = model(batch_x)

            # logits is [batch, seq_len, vocab_size], compute loss on last token prediction
            last_logits = logits[:, -1, :]
            loss = criterion(last_logits, batch_y)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / max(1, num_batches)
        scheduler.step(avg_loss)
        history.append({"epoch": epoch, "loss": round(avg_loss, 4)})

        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            print(f"Epoch [{epoch:02d}/{epochs:02d}] - Loss: {avg_loss:.4f} - LR: {optimizer.param_groups[0]['lr']:.6f}")

        if avg_loss < best_loss:
            best_loss = avg_loss

    duration = time.time() - start_time
    print(f"\nTraining completed in {duration:.2f}s | Best Loss: {best_loss:.4f}")

    # 5. Save model checkpoint
    checkpoint_path = os.path.join(CHECKPOINTS_DIR, "melodia_lstm_v1.pt")
    torch.save({
        "epoch": epochs,
        "model_state_dict": model.state_dict(),
        "vocab_size": vocab_size,
        "embedding_dim": embedding_dim,
        "hidden_dim": hidden_dim,
        "num_layers": num_layers,
        "final_loss": best_loss,
        "history": history,
        "timestamp": time.time(),
    }, checkpoint_path)
    print(f"Saved checkpoint to {checkpoint_path}")

    return checkpoint_path

if __name__ == "__main__":
    train_model()
