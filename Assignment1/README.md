# ReToNFA
This program simulates Finite State Automata (FSA). Input is a description of FSA in 
a text file. Model is being build and run a number of strings. For each string, the simulator outputs whether a string
belongs to the
respective language represented by the automaton or not as well as produce a trace of execution. 
The full description is written in [file](assignment_1.pdf).

# How does it work
Program consists of two main parts. First part of the program reads the number
of test cases from the file “input.txt”. Second part is used to execute test
cases. It consists of reading automata description, test input strings and evaluation
algorithm, all from the same file. Numbers are casted to integer values and
lines are saved into lists with comma as a separator character. Evaluation
algorithm is executed as many times as the number of test strings. Every
character in the test string with initial state is searched in the transitions list. It
is searching the state, called the “next state” in program, to which the input
character leads from the initial state. Then the initial state of automaton
becomes the “current” state and the program is repeating. The last state is meant
as the "final" state and if it is situated in the list of final states and if it belongs
to the language defined by the automaton, “True” is printed to the
“output.txt” file, otherwise “False” is printed.
The automaton was tested on different sets of strings, including empty strings,
example automata descriptions and no errors was detected.
