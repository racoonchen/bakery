# -*- encoding: utf_8 -*-
# tokenizer 1.2 (без < >, знаки препинания сохраняются как токены)
import codecs
#split_token = [u'.', u',', u' ', u':', u';', u"'", u'"', u'?', u'!', u'(', u')', u'\n', u'\t', u'/', u'\\']
split_token = [u' ', u'\t', u'/', u'\\']
weg = [u' ', u'\n', u'\t', u'-', u'\r'] #'"', '(', ')', '.', ',', '?', '!'] 	# ? u'\xa0'
punct = [u',', u':', u';', u'(', u')', u'-', u"'", u'"']
split_sent = [u'.', u'!', u'?', u'\n']
roman = [u'I', u'V', u'X', u'L', u'M']

def strip_string(string):
	if len(string)>1:
		while len(string)>1 and (string[0] in weg or string[len(string)-1] in weg):
			for item in weg: string = string.strip(item)
	return string

def is_number(token):
	if token.isdigit(): return True 
	elif token in roman: return True
	else: return False
	
def tokenizer(s):
	tokens = []
	word = u''
	for symbol in s:
		if symbol in punct and len(word) > 0:
			word = strip_string(word)
			if len(word) > 0 and word not in split_token:
				tokens.append(word)
				word = u''
			tokens.append(symbol)
		elif symbol in split_sent:
			word = strip_string(word)
			if len(word) > 0 and word not in split_token:
				tokens.append(word)
				word = u''
			tokens.append('*')
		elif symbol in split_token and len(word) > 0:
			word = strip_string(word)
			if len(word) > 0 and word not in split_token:
				tokens.append(word)
				word = u''
		else: word = word + symbol
	return tokens
	
def tokenize(text):
	print u'Tokenization in process...'
	list_of_lines = text.readlines()
	all_tokens = []
	for line in list_of_lines:
		tokens = tokenizer(line)
		for token in tokens:
			all_tokens.append(token)
	
	print u'Tokenization done.'
	return all_tokens