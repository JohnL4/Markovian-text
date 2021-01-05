#!/usr/local/bin/python3

import argparse, collections, random

parser = argparse.ArgumentParser(description='Generate order-k Markovian text given input sample text file')
parser.add_argument('--sampleFile', type=open, required=True,
                    help='File containing sample text.  Line terminators will be preserved')
parser.add_argument('--preserveLineBreaks', action='store_true',
                    help='Preserve line breaks in input; otherwise just treat them as a space character')
parser.add_argument('-k', type=int, default=3)
# parser.add_argument('--startOn', type=str, choices=['word', 'capitol', 'line', 'any'], default='word',
#                     help='Start generating on the given boundary (or none); governs random choice of first character ("capitol" is capitol letter beginning word)')
parser.add_argument('--terminateOn', '--endOn', choices=['EOL', 'EOP', 'length'], default='length',
                    help='The condition on which to terminate the generated text -- End of Line, End of Paragraph, or length of output (in characters)')
parser.add_argument('--terminateLength', '--length', type=int, default=50,
                    help='If --terminateOn is "length", the number of characters to output before terminating')
args = parser.parse_args()


#----------------------------------------------------  MarkovDict  -----------------------------------------------------

class MarkovDict:
   """
   A "dictionary" of frequency tables, mapping from a prefix string of characters (possibly 0-length) to a frequency table
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

   def nextRandomChar( self, aTextSoFar: str) -> str:
      """Return a random next character, given the aTextSoFar."""
      n = min( self.order(), len(aTextSoFar))
      # prefix will be last k characters of text so far, where k is order.
      prefix = aTextSoFar[ len( aTextSoFar) - n :len( aTextSoFar)]
      freqTable = self._prefixToFreqTable[ prefix]
      # TODO: precompute or cache the following sum
      totFreq = sum( freqTable.values())
      r = random.randrange( totFreq)
      for (k,v) in freqTable.items():
         nextChar = k
         r -= v
         if (r < 0):
            break
      return nextChar

#-------------------------------------------------------  main  --------------------------------------------------------

def main():
   if args.terminateOn in [ 'EOL', 'EOP'] and not args.preserveLineBreaks:
      raise Exception( '--terminateOn EOL or EOP requires --preserveLineBreaks')

   markovDict = MarkovDict( args.k)

   readSample( markovDict)

   s = random.seed()

   generatedText = ''
   while (not stop( generatedText)):
      generatedText += markovDict.nextRandomChar( generatedText)
   print( generatedText.rstrip())

def stop( aTextSoFar: str) -> bool:
   if (args.terminateOn == 'EOP'):
      retval = aTextSoFar.endswith('\n\n')
   elif (args.terminateOn == 'EOL'):
      retval = aTextSoFar.endswith( '\n')
   elif (args.terminateOn == 'length'):
      retval = len( aTextSoFar) >= args.terminateLength
   return retval

def readSample( aMarkovDict: MarkovDict) -> None:
   """Read the given sample file into the given MarkovDict."""
   print( f'Reading {args.sampleFile.name} into MarkovDict of order {aMarkovDict.order()}')
   lineEnd = '\n' if args.preserveLineBreaks else ' '
   filePrefix = ''
   prevChars = collections.deque()
   for line in args.sampleFile:
      line = line.rstrip()
      if len( filePrefix) < aMarkovDict.order():
         filePrefix += line[0:aMarkovDict.order()]
         if len( filePrefix) < aMarkovDict.order():
            # Still too short; more characters might be coming from the next line, so slap on a lineEnd.
            filePrefix += lineEnd
      for char in line:
         analyzePrevChars( aMarkovDict, prevChars, char)
         pushChar( prevChars, char, aMarkovDict.order())
      analyzePrevChars( aMarkovDict, prevChars, lineEnd)
      pushChar( prevChars, lineEnd, aMarkovDict.order())
   # Loop around to beginning of file a bit so if we randomly get a sequence of characters at the end of the file, we 
   # don't bomb out because that sequence isn't in the MarkovDict.
   for char in filePrefix:
      analyzePrevChars( aMarkovDict, prevChars, char)
      pushChar( prevChars, char, aMarkovDict.order())

def analyzePrevChars( aMarkovDict: MarkovDict, aPrevChars: collections.deque, aChar: str) -> None:
   """Analyze the given string of characters into the given MarkovDict."""
   prefixes = prefixesFromDeque(aPrevChars)
   for pfx in prefixes:
      aMarkovDict.add(aChar, pfx)
   while (len( aPrevChars) > aMarkovDict.order()):
      aPrevChars.popleft()

def prefixesFromDeque( aDequeOfChars: collections.deque) -> [str]:
   """
   A list of prefixes from the given deque, including the last char.  Prefixes are built from the right, so if the
   current deque is ['a','b','c'], the returned prefixes will be ['', 'c', 'bc', 'abc'].
   """ 
   retval = [] 
   for i in range( len( aDequeOfChars) + 1):  
      pfx = "" 
      for j in range(i):  
         pfx = aDequeOfChars[ -j - 1 ] + pfx
      retval.append( pfx) 
   return retval

def pushChar( aDequeOfChars: collections.deque, aChar: str, aMaxLength: int) -> None:
   """Push the given char onto the deque, keeping the length of the deque no more than aMaxLength."""
   aDequeOfChars.append( aChar)
   while (len( aDequeOfChars) > aMaxLength):
      aDequeOfChars.popleft()

#----------------------------------------------------  call main()  ----------------------------------------------------

if __name__ == '__main__':
   main()
