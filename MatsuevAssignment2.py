#!/usr/bin/python

import os

class Trans():
	def __init__(self, vf, vt, symbol):
		self.vertex_from=vf
		self.vertex_to=vt
		self.trans_symbol=symbol

	def __repr__(self):
		return str(self.vertex_from)+"->"+str(self.vertex_to)+'('+str(self.trans_symbol)+')'

class NFA(object):
	fs=0
	vertex=[]
	transitions=[]

	def __init__(self):
		self.transitions=[]
		self.fs=0
		self.vertex=[]

	def get_vertex_count(self):
		"""Amount of vertexes in an automaton"""
		return len(self.vertex)

	def set_final_state(self,num):
		self.fs = num

	def get_final_state(self):
		return self.fs

	def set_vertex(self, iter):
		# Increments on iter amount of transitions
		[self.vertex.append(i) for i in range(iter)]

	def set_transition(self, vertex_from, vertex_to, symbol):
		new_trans=Trans(vertex_from, vertex_to, symbol)
		self.transitions.append(new_trans)

	def display(self):
		print self.transitions

def concat(to,b):
	"""Merges two NFAs"""
	# To is the first one, b is the second one
	result = NFA()
	toAmountVertexes= to.get_vertex_count()
	bAmountVertexes= b.get_vertex_count()
	result.set_vertex(toAmountVertexes + bAmountVertexes-1)

	# Shifting states number on 1
	for transition in to.transitions:
		result.set_transition(transition.vertex_from, transition.vertex_to, transition.trans_symbol)
		toLastVertex=transition.vertex_to

		# Shifting states number according to "to" automaton
	for transition in b.transitions:
		result.set_transition(transition.vertex_from+toLastVertex, \
			transition.vertex_to+to.get_vertex_count()-1, transition.trans_symbol)
		bLastVertex=transition.vertex_to+toLastVertex

	result.set_final_state(bLastVertex)

	return result

def kleene(a):

	result = NFA()
	result.set_vertex(a.get_vertex_count() + 2)
	result.set_transition(0, 1, '^')

	for i in range(len(a.transitions)):
		new_trans = a.transitions[i]
		result.set_transition(new_trans.vertex_from + 1, new_trans.vertex_to + 1, new_trans.trans_symbol)

	result.set_transition(result.transitions[-1].vertex_to, a.get_vertex_count() + 1, '^')
	result.set_transition(result.transitions[-2].vertex_to, 1, '^')
	result.set_transition(0, a.get_vertex_count() + 1, '^')
	result.set_final_state(a.get_vertex_count() + 1)

	return result

def or_selection(to, b):
	# additional vertexes
	vertex_count = 2
	result = NFA()
	adder = 1

	result.set_vertex(vertex_count + to.get_vertex_count() + b.get_vertex_count())
	result.set_transition(0, adder, "^")

	for transition in to.transitions:
		result.set_transition(transition.vertex_from+adder, transition.vertex_to + adder, transition.trans_symbol)
	
	result.set_transition(result.transitions[-1].vertex_to,to.get_vertex_count()+1,"^")
	adder+=vertex_count+to.get_vertex_count()-1
	result.set_final_state(result.transitions[-1].vertex_to)
	result.set_transition(0, adder, "^")

	for transition in b.transitions:
		result.set_transition(transition.vertex_from+adder, transition.vertex_to + adder, transition.trans_symbol)
	
	result.set_transition(result.transitions[-1].vertex_to,to.get_vertex_count()+1,"^")
	adder+=result.get_vertex_count()

	return result

class ReToNFA(object):
	"""Make NFA from regexp"""
	solutionTrace=[]
	global_iter=-1
	fSolutionFound=False
	nfa=NFA()
	# operators are: "(|"
	# operators = []
	# operands consist of small NFAs
	operands = []
	nfa=NFA()

	def __init__(self, re):
		self.re = re
		# Calling function to create an automaton
		self.parse()
		self.solutionTrace=[]
		self.global_iter=-1
		self.fSolutionFound=False

	def test(self, test_string, outfile):
		trace=[]
		self.fSolutionFound=False
		self.solutionTrace=[]
		# the first initial state is zero
		trace.append(0)
		self.search_trace(test_string[:],trace)
		if self.solutionTrace:
			# If there is a solution
			outfile.write(" ".join('q'+str(i) for i in self.solutionTrace))
			outfile.write("\n")
		else:
			# If there is no solution
			outfile.write("\n")

	def search_trace(self, test_string, trace):
		"""Validation of input string checker"""
		for symbol in test_string:
			# If end of the string
			if symbol in "\n":
				# If last state in trace is the final one
				if trace[-1]==self.nfa.get_final_state():
					self.fSolutionFound=True
					# copying trace to solution trace ie result of executing
					self.solutionTrace=trace[:]
					return trace
				# if there is any epsilon transactions after \n symbol
				self.do_last_epsilon_transactions(test_string, trace)
				return
			# The state, we're searching for
			from_state=str(trace[-1])
			# Search in all possible transitions if vertex_from equals from_state
			# DFA algorithm
			for transition in self.nfa.transitions:					
				if str(transition.vertex_from)==from_state \
				and (symbol==str(transition.trans_symbol) or transition.trans_symbol=="^"):
					# Try this state
					trace.append(transition.vertex_to)
					# The transition is found
					if transition.trans_symbol=="^":
						# Passing independent copy of trace
						# and the same test string
						self.search_trace(test_string,trace[:])
					else:
						# passing test string without the first symbol
						self.search_trace(test_string[1:],trace[:])
					# Untry this state
					trace.pop()
					# Update from_state
					from_state=str(trace[-1])
					# If solution is found there is no need to search futher
					if self.fSolutionFound:
						return 
			# No transition fits to this input symbol and not the last symbol
			if transition==self.nfa.transitions[-1] and symbol != "\n":
				return

			# The state we're searching is the same as last recorded state and it is not a final one
			if str(trace[-1])==from_state and not trace[-1]==self.nfa.get_final_state():
				return
			
	def do_last_epsilon_transactions(self, test_string, trace):
		from_state=str(trace[-1])
		for transition in self.nfa.transitions:					
			if str(transition.vertex_from)==from_state and transition.trans_symbol=="^":
				trace.append(transition.vertex_to)
				if transition.trans_symbol=="^":
					self.search_trace(test_string,trace)
				trace.pop()

	def parse(self):
		# Amount of operands in list in every execution
		counter_operands=0
		self.solutionTrace=[]
		self.nfa= self.parse_inside(counter_operands)
		self.nfa.display()
		# Detecting loop and removing the one which vertex_from the biggest
		for transition2 in self.nfa.transitions:
			for transition in self.nfa.transitions:
				if transition.vertex_from==transition2.vertex_to\
				and transition.vertex_to==transition2.vertex_from\
				and transition.trans_symbol=="^"\
				and transition2.trans_symbol=="^":
					if transition.vertex_from>transition2.vertex_to:
						self.nfa.transitions.remove(transition)
					else:
						self.nfa.transitions.remove(transition2)


	def parse_inside(self, counter_operands):
		"""Function for parsing regular expression"""
		operators=[]
		while self.global_iter<len(self.re)-1:
			self.global_iter+=1
			cur_sym=self.re[self.global_iter]

			if cur_sym not in "()*|\n":
				tempnfa = NFA();
				tempnfa.set_vertex(2);
				tempnfa.set_transition(0, 1, cur_sym)
				tempnfa.set_final_state(1)
				self.operands.append(tempnfa)
				counter_operands+=1
				# If there was three operands, two of them can be merged
				if counter_operands==3 and not operators:
					op3 = self.operands.pop()
					op2,op1=self.take_two_top_operands()
					self.operands.append(concat(op1, op2));
					self.operands.append(op3);
					counter_operands=2

				if operators and operators[-1]=='|':
					operators.pop()
					op2,op1=self.take_two_top_operands()
					self.operands.append(or_selection(op1,op2))
					counter_operands-=1
				
			else:
				if(cur_sym == '*'):
					star=self.operands.pop();
					self.operands.append(kleene(star))
					
				elif cur_sym == '|':
					counter_operands+=1
					self.parse_inside(0)
					operators.append(cur_sym)

				elif cur_sym == '(':
					counter_operands+=1
					# Calling itself resetting counter of operands
					self.parse_inside(0)

				elif cur_sym in "\n)|":
					# merging two operands by union
					while operators and operators[-1]=='|':
						operators.pop()
						op2,op1=self.take_two_top_operands()
						self.operands.append(or_selection(op1,op2))
						counter_operands-=1

					while counter_operands>=2:
						op2,op1=self.take_two_top_operands()
						self.operands.append(concat(op1, op2));
						counter_operands-=1

					if counter_operands<2:
						return self.operands[-1]

					else: return self.operands[-1]

	def take_two_top_operands(self):
		op2 = self.operands[-1]
		self.operands.pop()
		op1 = self.operands[-1]
		self.operands.pop();
		return op2,op1
def testing():
	with open("input.txt",'r') as infile:
		f = open('output.txt', 'w')
		regexp=infile.readline().strip()
		regexp+='\n'
		nfa = ReToNFA(str(regexp))
		number_tests=int(infile.readline().strip())
		for i in range(number_tests):
			test_string=infile.readline().strip()
			# Paste \n if it not in test string
			if '\n' not in test_string:
				test_string+='\n'
			nfa.test(str(test_string),f)
		# deleting last symbol in file
		f.seek(-1, os.SEEK_END)
		f.truncate()

if __name__ == "__main__":
	# main routines here
	testing()