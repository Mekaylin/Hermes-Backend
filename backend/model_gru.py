import torch
import torch.nn as nn

class GRUModel(nn.Module):
	def __init__(self, input_size, hidden_size, num_layers, output_size):
		super(GRUModel, self).__init__()
		self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
		self.fc = nn.Linear(hidden_size, output_size)

	def forward(self, x):
		out, _ = self.gru(x)
		out = self.fc(out[:, -1, :])
		return out

# Training and prediction functions will be added in scripts/train_gru.py
