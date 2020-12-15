#!/usr/local/bin/python3

import argparse, collections

#----------------------------------------------------  MarkovDict  -----------------------------------------------------

class MarkovDict:
   """
   A "dictionary" of frequency tables, mapping from a 23 of characters (possibly 0-length) to a frequency table
   of characters that follow that prefix.
   """
   def __init__( self, k: int):
      self._order = k
      self._prefixToFreqTable = {}

   def order( self) -> int:
      """Return the 'order' of this MarkovDict, where 'order' is a non-negative integer."""
      return self._order

   def add( self, aChar: str, aPrefix: str) -> None:
      """
      Add the given character to the frequency tables of this MarkovDict by bumping the count by 1 for the given prefix
      and character.
      """
      if (aPrefix not in self._prefixToFreqTable):
         self._prefixToFreqTable[aPrefix] = {}
      if (aChar not in self._prefixToFreqTable[ aPrefix]):
         self._prefixToFreqTable[ aPrefix][ aChar] = 0
      self._prefixToFreqTable[ aPrefix][ aChar] += 1

   def nextChar( self, prefix: str) -> str:
      """Return a random next character, given the prefix."""
      return 'a'


#-------------------------------------------------------  main  --------------------------------------------------------

def main():
   parser = argparse.ArgumentParser( description='Generate order-k Markovian text given input text file')
   parser.add_argument( '--sampleFile', type=open, required=True,
      help='File containing sample text.  Line terminators will be preserved')
   parser.add_argument( '-k', type=int, default=3)
   parser.add_argument( '--terminateOn', '--endOn', choices=['EOL','EOP','length'], default='length',
      help='The condition on which to terminate the generated text -- End of Line, End of Paragraph, or length of output (in characters)')
   parser.add_argument( '--terminateLength', '--length', type=int, default=50,
      help='If --terminateOn is "length", the number of characters to output before terminating')
   args = parser.parse_args()

   print( f'Input\t: {args.sampleFile.name}')
   print( f'k\t: {args.k}')
   print( f'terminateOn\t: {args.terminateOn}')
   print( f'terminateLength\t: {args.terminateLength}')

   markovDict = MarkovDict( args.k)

   readSample( args.sampleFile, markovDict)

   raise "Finish writing main(), ya dummy!"

def readSample( aFile, aMarkovDict: MarkovDict) -> None:
   """Read the given sample file into the given MarkovDict."""
   print( f'Reading {aFile.name} into MarkovDict of order {aMarkovDict.order()}')
   prevChars = collections.deque()
   prefixes = ['']
   for line in aFile:
      line = line.rstrip()
      for char in line:
         analyzePrevChars( aMarkovDict, prevChars, char)
         pushChar( prevChars, char, aMarkovDict.order())
      analyzePrevChars( aMarkovDict, prevChars, '\n')
      pushChar( prevChars, '\n', aMarkovDict.order())

def analyzePrevChars( aMarkovDict: MarkovDict, aPrevChars: collections.deque, aChar: str) -> None:
   """Analyze the given string of characters into the given MarkovDict."""
   prefixes = prefixesFromDeque(aPrevChars)
   for pfx in prefixes:
      aMarkovDict.add(aChar, pfx)
   while (len( aPrevChars) > aMarkovDict.order()):
      aPrevChars.popleft()

def prefixesFromDeque( aDequeOfChars: collections.deque) -> [str]:
   """A list of prefixes from the given deque, including the last char."""
   retval = []
   for i in range( len( aDequeOfChars)):
      pfx = ''
      for j in range(i):
         pfx += aDequeOfChars[j]
      retval += pfx
   return retval

def pushChar( aDequeOfChars: collections.deque, aChar: str, aMaxLength: int) -> None:
   """Push the given char onto the deque, keeping the length of the deque no more than aMaxLength."""
   aDequeOfChars.append( aChar)
   while (len( aDequeOfChars) > aMaxLength):
      aDequeOfChars.popleft()

#----------------------------------------------------  call main()  ----------------------------------------------------

if __name__ == '__main__':
   main()
