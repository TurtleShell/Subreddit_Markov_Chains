#package subredditSim

import sys
import random
import praw

class PathNode:

	def __init__(self):
		self.next_word_list = dict()
		self.total_next_words = 0

	def add_next_word(self, next_word):
		if next_word in self.next_word_list:
			self.next_word_list[next_word] += 1
		else :
			self.next_word_list[next_word] = 1

		self.total_next_words += 1

	def pick_next_word(self):
		int_result = random.randrange(self.total_next_words)
		weight_total = 0

		for word in self.next_word_list:
			my_weight = self.next_word_list[word]
			weight_total = weight_total + my_weight
			if int_result <= weight_total:
				return word


	def __str__(self):
		return str(self.next_word_list)

class WordHashTable:

	def __init__(self):
		self.hashTable = dict()

	def submit_words(self, word_from, word_to):
		if word_from in self.hashTable:
			current_pathNode = self.hashTable[word_from]
			current_pathNode.add_next_word(word_to)
		else:
			newPathNode = PathNode()
			newPathNode.add_next_word(word_to)
			self.hashTable[word_from] = newPathNode

	def get_pathNode(self, word):
		result = self.hashTable[word]
		return result

	def __str__(self):
		result = ""
		for key in self.hashTable:
			result += "key: " + key + "\n"
			current_pn = str(self.hashTable[key])
			result += "PathNode: " + current_pn + "\n\n"

		return result


def generate_hashtable(subreddit, submission_limit):

	submissions = subreddit.get_hot(limit=submission_limit)

	hashtable = WordHashTable()

	for submission in submissions:
		#print ("sub posts:\n", submission.title)

		sub_title = submission.title.split(' ')

		previous_word = "title_start_string"

		for word in sub_title:
			hashtable.submit_words(previous_word, word)

			previous_word = word

		hashtable.submit_words(previous_word, "title_end_string")

	return hashtable


def generate_sentence(hashtable):

	result = ""
	current_word = "title_start_string"
	#while current_word != "title_end_string":
	while True:
		current_pathNode = hashtable.get_pathNode(current_word)

		next_word = current_pathNode.pick_next_word()

		if next_word == "title_end_string":
			break

		result += next_word
		result += " "

		current_word = next_word

	return result


def main():
	
	sub_name = sys.argv[1]
	submission_limit = int(sys.argv[2])

	r = praw.Reddit(user_agent='subredditSim')

	selected_subreddit = r.get_subreddit(sub_name)

	hashtable = generate_hashtable(selected_subreddit, submission_limit)
	#print ("\nhashtable:\n", hashtable)

	sentence = generate_sentence(hashtable)
	print ("\nsentence:\n", sentence)


if __name__ == "__main__":
	main()
