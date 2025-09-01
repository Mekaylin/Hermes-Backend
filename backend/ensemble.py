
def combine_signals(gru_signal, sentiment_scores):
	# Simple ensemble: if sentiment is mostly positive, bias toward buy; negative, bias toward sell
	pos = sentiment_scores.count(2)
	neg = sentiment_scores.count(0)
	if pos > neg:
		return "buy"
	elif neg > pos:
		return "sell"
	else:
		return gru_signal
