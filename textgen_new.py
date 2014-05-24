# -*- encoding: utf-8 -*-
import os, codecs, random, nltk
from nltk.probability import LidstoneProbDist  
from nltk.model import NgramModel  
from tokenization2 import tokenize, strip_string

# подсчет гласных, определение положения ударения
def count_vowels(s):
	number_of_v = 0
	stress_position = None # по умолчанию: ударение не проставлено
	for i in s:
		if i in vowels: number_of_v += 1
		elif i == "<": stress_position = number_of_v
	if stress_position == None and number_of_v > 0: stress_position = 1 # односложные слова
	elif number_of_v == 0: stress_position = 0 # слова без гласных
	return number_of_v, stress_position

def it_is_a_pretty_yamb(line, stress_position, number_of_v):
	if stress_position == None: # если ударение не проставлено, слово нам не подходит
		return False
	else:
		line_number_of_v = count_vowels(line)[0]
# слово принимается в следующих случаях:
# 1. четность количества гласных в строке совпадает с четностью позиции ударения в слове
# 2. слово односложное или без гласных
		if (line_number_of_v % 2 == stress_position % 2) or (number_of_v == 0) or (number_of_v == 1):
			return True
		else:
			return False

## генерируем первое слово для контекста "*" (начало предложения)
def generate_first_word(list_of_words):
	random_word = random.choice(list_of_words)
	number_of_v, stress_position = count_vowels(random_word)
	while (number_of_v >= 9) or (not it_is_a_pretty_yamb("", stress_position, number_of_v)) or (random_word in forbidden_words) or (random_word in prepositions):
		print u'Searching for first word...'
		#random_word = random.choice(list_of_words)
		random_word = model.generate(1, context = u'*')[0]
		number_of_v, stress_position = count_vowels(random_word)
	print u'Random word generated.'
	return random_word

# чтобы ямб звучал нормально, последний четный слог строки должен быть ударным
def ends_correctly(possible_line, last_even_vowel):
	i = 0
	len = 0
	for char in possible_line:
		len += 1
		if char in vowels:
			i += 1
			if i == last_even_vowel:
				try:
					if possible_line[len] == "<": return True
					else: return False
				except: # если ударение не на конце, possible_line[len] может не существовать
					return False
	
# запрет на несуществующие слова, на 2 одинаковых слова подряд, на 2 предлога\союза подряд				
def is_allowed_word_combination(previous_word, next_word):
	if next_word in forbidden_words: return False
	elif previous_word == next_word: return False
	elif previous_word in prepositions and next_word in prepositions: return False
	else: return True
	
#генерируем строку, начинающуюся с word, с i слогов (т.е. i гласных) и возвращаем ее в виде списка слов
def generate_line(meisterwerk, i):
	line = []
	last_even_vowel = i-i%2 # т.е. 8й гласный
	vowels = number_of_attempts = 0
	context_length = 5
	final_preposition = False
	previous_word = meisterwerk[-1]
	while vowels < i or final_preposition == True:
		joined_line = "".join(w for w in line)
		#print str(number_of_attempts)
		
		if number_of_attempts < 30:
			next_word = model.choose_random_word(context = meisterwerk[-context_length:])
		#	next_word = model.generate(1, context = meisterwerk[-context_length:])[0]
		elif number_of_attempts < 50:
			next_word = model.choose_random_word(context = previous_word)
		else: next_word = random.choice(all_tokens)
		
		number_of_attempts += 1
		number_of_v, stress_position = count_vowels(next_word)
		if is_allowed_word_combination(previous_word, next_word) and vowels + number_of_v <= i and it_is_a_pretty_yamb(joined_line, stress_position, number_of_v):
			if vowels+number_of_v < last_even_vowel or ends_correctly(joined_line+next_word, last_even_vowel):
				line.append(next_word)
				meisterwerk.append(next_word)
				vowels = vowels+number_of_v
				previous_word = next_word
				number_of_attempts = 0
				print u'Next word generated'

		## слово не должно заканчиваться на предлог
		if number_of_v == i:
			if line[-1] in prepositions: 
				final_preposition = True
	return line

# выполнение программы теперь в цикле, это ни на что не влияет, но так вроде бы принято :)
# к тому же если мы захотим импортировать этот скрипт или что-то из него, проблем будет меньше
if __name__ == "__main__":
	# input - на входе текст с проставленными ударениями ('<')
	text_name = u'10_corpus_wa_ed'
	scriptdir = os.path.dirname(os.path.realpath(__file__))
	scriptdir = scriptdir.replace("\\", "/")+"/"
	text_path = scriptdir + text_name + '.txt'
	text = codecs.open(text_path, 'r', encoding = 'utf-8')
	# output
	out_text_path = scriptdir + u'generated_from_' + text_name + u'.txt'
	out_text = codecs.open(out_text_path, u'w', encoding = 'utf-8')
	# список гласных
	vowels_doc = codecs.open(scriptdir + u'vowels.txt', u'r', encoding = 'utf-8')
	vowels = vowels_doc.readline()
	# список запрещенных слов ("т", "д" и т.п.)
	forbidden_words_doc = codecs.open(scriptdir + u'forbidden_words.txt', u'r', encoding = 'utf-8')
	forbidden_words = forbidden_words_doc.readline()
	# список предлогов и других служебных слов
	prep_doc = codecs.open(scriptdir + u'prepos_list.txt', u'r', encoding = 'utf-8')
	prepositions = []
	for line in prep_doc:
		if len(line)>0: prepositions.append(strip_string(line))
		
	# Представляем входной текст в виде списка токенов
	all_tokens = tokenize(text)

	# строим языковую модель
	ngrams = 10
	estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.1)  
	model = NgramModel(ngrams, all_tokens, estimator=estimator)
	print 'Language model built.'
	
	# рандомно генерируем первое слово
	random_word = generate_first_word(all_tokens)
	meisterwerk = [random_word]
	
	# генерируем 4 строки. Количество слогов по строкам: 9/8/9/8
	first_line = generate_line(meisterwerk, 9)
	for word in first_line: meisterwerk.append(word)
	print '1st line generated.'
	
	second_line = generate_line(meisterwerk, 8)
	for word in second_line: meisterwerk.append(word)
	print '2nd line generated.'
	
	third_line = generate_line(meisterwerk, 9)
	for word in third_line: meisterwerk.append(word)
	print '3rd line generated.'
	
	fourth_line = generate_line(meisterwerk, 8)
	for word in fourth_line: meisterwerk.append(word)
	print '4th line generated.'
	
	pirozhok = ' '.join([word for word in first_line]) + u'\n' + ' '.join([word for word in second_line]) + u'\n' + ' '.join([word for word in third_line]) + u'\n' + ' '.join([word for word in fourth_line]) + u'\npirozhok-generator(c)'
	## удаляем знак ударения
	pirozhok = pirozhok.replace('<', '')
	# записываем текст в новый файл
	out = pirozhok.encode(u'utf-8').decode(u'utf-8', u'ignore')
	out_text.write(out)
	print 'Text generated (' + out_text_path + u').'