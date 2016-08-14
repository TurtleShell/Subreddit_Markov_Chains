#package subredditSim

import sys
import random
import praw

class WordPair:

	def __init__(self, first_word, second_word):
		self.first_word = first_word
		self.second_word = second_word

	def __eq__(self, other):
		if (self.first_word == other.first_word) and (self.second_word == other.second_word):
			return True
		else:
			return False

	def __hash__(self):
		return hash(str(self))

	def __str__(self):
		result = "{" + self.first_word + "-->" + self.second_word + "}"
		return result

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

	def submit_wordpair(self, wordpair_from, word_to):
		if wordpair_from in self.hashTable:
			current_pathNode = self.hashTable[wordpair_from]
			current_pathNode.add_next_word(word_to)
		else:
			newPathNode = PathNode()
			newPathNode.add_next_word(word_to)
			self.hashTable[wordpair_from] = newPathNode

	def get_pathNode(self, wordpair):
		#print ("is wordpair in hashTable? ", wordpair in self.hashTable)
		result = self.hashTable[wordpair]
		return result

	def __str__(self):
		result = ""
		for key in self.hashTable:
			result += "key: " + str(key) + "\n"
			current_pn = str(self.hashTable[key])
			result += "PathNode: " + current_pn + "\n\n"

		return result


def generate_hashtables(subreddit, submission_limit):

	submissions = subreddit.get_hot(limit=submission_limit)

	subset = set()

	hashtable = WordHashTable()

	for submission in submissions:
		#print ("sub posts:\n", submission.title)

		sub_title = submission.title.lower()
		subset.add(sub_title)

		sub_split = sub_title.split(' ')

		prev_word = "pre_title_start_string"
		cur_word = "title_start_string"
		cur_wordpair = WordPair(prev_word, cur_word)

		for next_word in sub_split:

			hashtable.submit_wordpair(cur_wordpair, next_word)

			prev_word = cur_word
			cur_word = next_word
			cur_wordpair = WordPair(prev_word, cur_word)

		hashtable.submit_wordpair(cur_wordpair, "title_end_string")

	return (hashtable, subset)


def generate_sentence(hashtable):

	result = ""
	prev_word = "pre_title_start_string"
	cur_word = "title_start_string"
	cur_wordpair = WordPair(prev_word, cur_word)

	while True:
		#print ("searching for wordpair: ", cur_wordpair)
		current_pathNode = hashtable.get_pathNode(cur_wordpair)

		next_word = current_pathNode.pick_next_word()

		if next_word == "title_end_string":
			result = result[0:-1]
			break

		result += next_word
		result += " "

		prev_word = cur_word
		cur_word = next_word
		cur_wordpair = WordPair(prev_word, cur_word)

	return result


def main():
	
	sub_name = sys.argv[1]
	submission_limit = int(sys.argv[2])

	r = praw.Reddit(user_agent='subredditSim')

	selected_subreddit = r.get_subreddit(sub_name)

	hashresults = generate_hashtables(selected_subreddit, submission_limit)
	hashtable = hashresults[0]
	subset = hashresults[1]
	#print ("\nhashtable:\n", hashtable)

	#print ("subset: ", subset)

	sentence = ""
	while True:
		sentence = generate_sentence(hashtable)
		#print ("\nsentence:\n", sentence)
		if sentence not in subset:
			#print ("not in subset")
			break

	print ("\nsentence:\n", sentence)


if __name__ == "__main__":
	main()
