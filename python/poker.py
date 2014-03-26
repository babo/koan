#!/usr/bin/env python
'''
Copyright (c) 2011, attila.babo@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

--------------------

The Psychic Poker Player

In 5-card draw poker, a player is dealt a hand of five cards (which may be
looked at). The player may then discard between zero and five of his or her
cards and have them replaced by the same number of cards from the top of the
deck (which is face down). The object is to maximize the value of the final
hand. The different values of hands in poker are given at the end of this
problem.  Normally the player cannot see the cards in the deck and so must use
probability to decide which cards to discard. In this problem, we imagine that
the poker player is psychic and knows which cards are on top of the deck. Write
a program which advises the player which cards to discard so as to maximize the
value of the resulting hand.

Input and Output

Input will consist of a series of lines, each containing the initial five cards
in the hand then the first five cards on top of the deck. Each card is
represented as a two-character code. The first character is the face-value
(A=Ace, 2-9, T=10, J=Jack, Q=Queen, K=King) and the second character is the suit
(C=Clubs, D=Diamonds, H=Hearts, S=Spades). Cards will be separated by single
spaces. Each input line will be from a single valid deck, that is there will be
no duplicate cards in each hand and deck.  Each line of input should produce one
line of output, consisting of the initial hand, the top five cards on the deck,
and the best value of hand that is possible. Input is terminated by end of file.
Use the sample input and output as a guide. Note that the order of the cards in
the player's hand is irrelevant, but the order of the cards in the deck is
important because the discarded cards must be replaced from the top of the deck.
Also note that examples of all types of hands appear in the sample output, with
the hands shown in decreasing order of value.

Sample Input

TH JH QC QD QS QH KH AH 2S 6S
2H 2S 3H 3S 3C 2D 3D 6C 9C TH
2H 2S 3H 3S 3C 2D 9C 3D 6C TH
2H AD 5H AC 7H AH 6H 9H 4H 3C
AC 2D 9C 3S KD 5S 4D KS AS 4C
KS AH 2H 3C 4H KC 2C TC 2D AS
AH 2C 9S AD 3C QH KS JS JD KD
6C 9C 8C 2D 7C 2H TC 4C 9S AH
3D 5S 2H QD TD 6S KH 9H AD QH

Sample Output

Hand: TH JH QC QD QS Deck: QH KH AH 2S 6S Best hand: straight-flush
Hand: 2H 2S 3H 3S 3C Deck: 2D 3D 6C 9C TH Best hand: four-of-a-kind
Hand: 2H 2S 3H 3S 3C Deck: 2D 9C 3D 6C TH Best hand: full-house
Hand: 2H AD 5H AC 7H Deck: AH 6H 9H 4H 3C Best hand: flush
Hand: AC 2D 9C 3S KD Deck: 5S 4D KS AS 4C Best hand: straight
Hand: KS AH 2H 3C 4H Deck: KC 2C TC 2D AS Best hand: three-of-a-kind
Hand: AH 2C 9S AD 3C Deck: QH KS JS JD KD Best hand: two-pairs
Hand: 6C 9C 8C 2D 7C Deck: 2H TC 4C 9S AH Best hand: one-pair
Hand: 3D 5S 2H QD TD Deck: 6S KH 9H AD QH Best hand: highest-card

Original problem description: http://uva.onlinejudge.org/external/1/131.html
'''

import os

class Card(object):
    '''Convert a card from input characters to a hexadecimal number with two digits
    Higher digit holds figure, always higher than zero.
    Lower digit holds suit, could be zero.'''

    _FIG = 'A23456789TJQK'
    _SUIT = 'CDHS'
    _CARD = dict(   [(figure, i << 4) for i, figure in enumerate(_FIG, 1)] + \
                    [(suit, i) for i, suit in enumerate(_SUIT, 1) ])

    def __init__(self, card):
        '''generate a single card as a hexadecimal number where
        lower digit contains suit as 1-4 figure encoded in higher
        digit from 1 to D'''
        self.card = self._CARD[card[0]] + self._CARD[card[1]]

    def __str__(self):
        '''Pretty print a card for debugging'''
        return self._FIG[self.figure_only()] + self._SUIT[self.suit_only()]

    def __int__(self):
        '''Raw integer representation of a card'''
        return self.card

    def suit_only(self):
        '''Strip of figure, returns a single integer from zero representing suit'''
        return (self.card & 0x0f) - 1

    def figure_only(self):
        '''Strip of suit, returns a single integer from zero representing figure'''
        return (self.card >> 4) - 1

class Hand(object):
    '''Represent a hand of cards'''

    _RANK = 'highest-card one-pair two-pairs three-of-a-kind straight flush full-house four-of-a-kind straight-flush'.split()

    def __init__(self, cards):
        self.cards = list(cards)
        self.rank = None

    def replace(self, index, c):
        '''Replace a card'''
        self.cards[index] = c
        self.rank = None

    def __str__(self):
        '''Represent a hand value as a string'''
        if not self.rank:
            self.rank = self.evaluate()
        return self.rank

    def __int__(self):
        '''Convert to a single integer to compare'''
        if not self.rank:
            self.rank = self.evaluate()
        return self._RANK.index(self.rank)

    def __ne__(self, other):
        '''Called by self != other operations'''
        return str(self) != str(other)

    def __gt__(self, other):
        '''Called by self > other operations'''
        return int(self) > int(other)

    @staticmethod
    def is_straight(figures):
        '''True for five consecutive figures'''
        stops = []
        for i in xrange(1, 5):
            if figures[i - 1] != figures[i] + 1:
                stops.append(i)
        return stops == [] or (stops == [4] and figures[0] == 12 and figures[4] == 0)

    def evaluate(self):
        '''Returns the best possible evaluation for a full hand'''
        suits = len(set(map(Card.suit_only, self.cards)))
        figures = sorted(map(Card.figure_only, self.cards), reverse=True)

        if suits == 1:
            return 'straight-flush' if self.is_straight(figures) else 'flush'
        if figures[0] == figures[3] or figures[1] == figures[4]:
            return 'four-of-a-kind'
        if figures[0] == figures[2] and figures[3] == figures[4]:
            return 'full-house'
        if figures[0] == figures[1] and figures[2] == figures[4]:
            return 'full-house'
        if self.is_straight(figures):
            return 'straight'
        if figures[0] == figures[2] or figures[1] == figures[3] or figures[2] == figures[4]:
            return 'three-of-a-kind'
        distinct = len(set(figures))
        if distinct == 3:
            return 'two-pairs'
        if distinct == 4:
            return 'one-pair'
        return 'highest-card'

def discard(n):
    '''Yield all possible combination of indexes to discard from hand'''
    if n > 0:
        s = []
        w = 0
        while True:
            for i in xrange(w, 5):
                s.append(i)
                w = i+1
                if len(s) == n:
                    yield s
                break
            else:
                if len(s):
                    w = s[-1]+1
                    del(s[-1])
                else:
                    break

def best_combinations(cards):
    '''Iterate all possible combinations (32)'''
    five = cards[:5]
    best = Hand(five)
    for d in xrange(1, 6):
        for variation in discard(d):
            hand = Hand(five)
            for n, r in enumerate(variation):
                hand.replace(r, cards[5+n])
            if hand > best:
                best = hand
    return best

def validate(cards):
    '''Validate a complete line of cards, hand and deck included
    returns either a list of cards or False'''
    return len(set(cards)) == 10 and cards

def convert(line):
    '''Convert an input line to cards as numbers'''
    try:
        return map(Card, line.upper().split())
    except:
        return []

def process(line):
    '''One line at a time'''
    cards = validate(convert(line))
    return cards and best_combinations(cards)

def read_input(fd):
    '''Loop over input lines'''
    while True:
        line = fd.readline()
        if not line:
            break
        print process(line.strip()) or 'Invalid line'

def test():
    '''Simple test data from original description'''
    data = \
        '''
        straight-flush
            TH JH QC QD QS QH KH AH 2S 6S
        four-of-a-kind
            2H 2S 3H 3S 3C 2D 3D 6C 9C TH
        full-house
            2H 2S 3H 3S 3C 2D 9C 3D 6C TH
        flush
            2H AD 5H AC 7H AH 6H 9H 4H 3C
        straight
            AC 2D 9C 3S KD 5S 4D KS AS 4C
        three-of-a-kind
            KS AH 2H 3C 4H KC 2C TC 2D AS
        two-pairs
            AH 2C 9S AD 3C QH KS JS JD KD
        one-pair
            6C 9C 8C 2D 7C 2H TC 4C 9S AH
        highest-card
            3D 5S 2H QD TD 6S KH 9H AD QH
        '''
    errors = 0
    result = None
    for line in data.split('\n'):
        line = line.strip()
        if result:
            r = process(line)
            if result != r:
                errors += 1
                print line, r, '<->', result
            result = None
        else:
            result = line
    return errors == 0

def main():
    '''Main entry point, reads stdin or a file if specified'''
    if not test():
        print 'Beware, not all tests passed!'
    if len(os.sys.argv) > 1 and os.path.isfile(os.sys.argv[1]):
        with open(os.sys.argv[1]) as fd:
            read_input(fd)
    else:
        read_input(os.sys.stdin)

if __name__ == '__main__':
    main()
