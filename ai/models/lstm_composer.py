import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple

class LSTMComposer(nn.Module):
    """
    Deep Learning Music Generation Model:
    Multi-layer Recurrent Neural Network (LSTM) with token embeddings and layer normalization
    for predicting sequential musical tokens.
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Token Embedding Layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        # 2-Layer LSTM with Dropout
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Normalization and Output Projection
        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(
        self,
        x: torch.Tensor,
        hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        x shape: [batch_size, seq_len]
        returns:
            logits: [batch_size, seq_len, vocab_size]
            hidden: (h_n, c_n)
        """
        # Embed tokens: [batch, seq_len, embedding_dim]
        embedded = self.embedding(x)

        # Pass through LSTM: [batch, seq_len, hidden_dim]
        lstm_out, hidden = self.lstm(embedded, hidden)

        # Normalize and apply dropout
        normed = self.layer_norm(lstm_out)
        dropped = self.dropout(normed)

        # Project to vocabulary logits: [batch, seq_len, vocab_size]
        logits = self.fc(dropped)

        return logits, hidden

    def sample_next_token(
        self,
        logits: torch.Tensor,
        temperature: float = 1.0,
        top_k: int = 8,
    ) -> int:
        """
        Samples the next token from logits using temperature scaling and top-k filtering.
        temperature: Controls randomness (lower = more conservative, higher = more experimental)
        top_k: Filters out tokens with low probability to prevent aberrant dissonances
        """
        # Scale by temperature
        temperature = max(0.1, min(temperature, 2.0))
        scaled_logits = logits / temperature

        # Top-k filtering
        if top_k > 0:
            top_k = min(top_k, scaled_logits.size(-1))
            values, indices = torch.topk(scaled_logits, top_k)
            # Mask out non-top-k logits
            filtered_logits = torch.full_like(scaled_logits, float("-inf"))
            filtered_logits.scatter_(-1, indices, values)
            scaled_logits = filtered_logits

        probabilities = F.softmax(scaled_logits, dim=-1)
        next_token = torch.multinomial(probabilities, num_samples=1).item()
        return next_token
