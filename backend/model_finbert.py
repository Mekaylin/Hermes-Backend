from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinBERTSentiment:
	def __init__(self):
		self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
		self.model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

	def predict_sentiment(self, text):
		inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
		outputs = self.model(**inputs)
		scores = torch.nn.functional.softmax(outputs.logits, dim=1)
		sentiment = torch.argmax(scores, dim=1).item()
		# 0: negative, 1: neutral, 2: positive
		return sentiment, scores.tolist()[0]
