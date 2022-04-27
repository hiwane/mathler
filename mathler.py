#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import doctest


class Mathler(object):

  def __init__(self, depth: int, ans: int):
    self.depth = depth
    self.op = {8: 3, 6: 2, 5: 1}[depth]  # max(# of operators)
    self.ans = ans
    self.reset()

  def _init_costs(self):
    self.cost = [0] * 10
    self.costs = [0] * self.depth
    for i in range(self.depth):
      self.costs[i] = [0] * 10

  def reset(self):
    self.out = set()
    self.hit = ['_'] * self.depth
    self.blow = [''] * self.depth
    self.stage = 0
    self.cand = []
    self._init_costs()

  def add(self, guess: str, response: str):
    if len(guess) != self.depth:
      raise ValueError('invalid guess(len): ' + guess)
    if len(response) != self.depth:
      raise ValueError('invalid response: ' + response)
    try:
      if self.parse(guess) != self.ans:
        raise ValueError('invalid guess(parse): ' + guess)
    except Exception:
      raise ValueError('invalid guess(parse): ' + guess)

    if len(set(response) - set('ox_- ')) != 0:
      raise ValueError('invalid response(parse): ' + response)

    for j in range(self.depth):
      if response[j] == 'o':  # hit
        assert self.hit[j] == '_' or self.hit[j] == guess[j]
        self.hit[j] = guess[j]
      elif response[j] == 'x':  # blow
        self.blow[j] += guess[j]
      else:
        self.out.add(guess[j])
    self.stage += 1

  def dprint(self, s):
    """for debug"""
    if False:
      print(s, file=sys.stderr)
    pass

  def lex(self, s):
    """lexer

    >>> w = Mathler(6, 6)
    >>> w.lex("1 3 45")
    [1, 3, 45]
    >>> w.lex("1 +- )3 4")
    [1, '+', '-', ')', 3, 4]
    """
    ret = []
    i = 0
    while i < len(s):
      if s[i] in [' ', '\t', '\n']:
        i += 1
        continue
      if s[i] in ['(', ')', '+', '-', '*', '/']:
        ret.append(s[i])
        i += 1
        continue
      v = 0
      j = i
      while i < len(s) and '0' <= s[i] <= '9':
        v = 10 * v + int(s[i])
        i += 1
      if i == j:
        raise Exception(f'unknown {s[j]}:{j}:{s}')
      if i - j >= 2 and s[j] == '0':
        raise Exception(f'unexpected 0 {s[j]}:{j}:{s}')
      ret.append(v)
    return ret

  def _factor(self, tokens, i):
    self.dprint(["_factor", i, tokens[i]])
    if isinstance(tokens[i], int):
      return tokens[i], i + 1
    if tokens[i] == '(':
      val, i = self._expr(tokens, i + 1)
      if tokens[i] != ')':
        raise Exception(f'expected ")", {tokens[i+1]},{i+1}')
      return val, i + 1
    raise Exception('expected "(", {tokens[1]},{i}')

  def _term(self, tokens, i):
    self.dprint(["_term", i, tokens[i]])
    val, i = self._factor(tokens, i)
    while i < len(tokens) and tokens[i] in ['*', '/']:
      op = tokens[i]
      v, i = self._factor(tokens, i + 1)
      if op == '*':
        val *= v
      elif v == 0:
        raise Exception('zero division')
      elif isinstance(val, int) and isinstance(v, int) and val % v == 0:
        val //= v
      else:
        val /= v
    return val, i

  def _expr(self, tokens, i):
    self.dprint(["_expr", i, tokens[i]])
    val, i = self._term(tokens, i)
    while i < len(tokens) and tokens[i] in ['+', '-']:
      op = tokens[i]
      v, i = self._term(tokens, i + 1)
      if op == '+':
        val += v
      else:
        val -= v
    return val, i

  def parse(self, s):
    """

    >>> w = Mathler(6, 9)
    >>> w.parse("3+4+5")
    12
    >>> w.parse("3-4+5")
    4
    >>> w.parse("5*8")
    40
    >>> w.parse("3+8/2")
    7
    >>> try: print(w.parse("83-3(/38"))
    ... except: print("except")
    except
    >>> try: print(w.parse("(99()*98"))
    ... except: print("except")
    except
    >>> try: print(w.parse("(9))*898"))
    ... except: print("except")
    except
    >>> w.parse("9*998/9")
    998
    """
    v = self.lex(s)
    self.dprint(["parse", s, v])
    val, i = self._expr(v, 0)
    if i != len(v):
      raise Exception('invalid')
    return val

  def _solve0(self, pp, s, op):
    if pp & set(s) != pp:
      return
    if self.stage <= 1 and op > 0:
      # 列挙削減のため，演算子数が最大なものを採用
      return
    try:
      v = self.parse(s)
      if -0.001 < v - self.ans < 0.001:
        self.cand.append(s)
    except Exception:
      pass
    return

  def _solve(self, depth, op, vv, hit, blow, pp, s, algo):
    if depth == 0:
      return self._solve0(pp, s, op)
    if self.stage <= 1 and depth < 2 * op:  # 全部の op を使い切ること.
      return

    n = len(s) - 1

    # 計算量削減のため不要なものは取り除く
    if hit[n + 1] != '_':
      v = set(hit[n + 1])
    elif n == -1 or s[n] in '+-/*(':  # 1文字目は数字か開括弧
      v = vv - set('+-/*)')
    elif (s[n] == '0' and (n == 0 or not ('0' <= s[n - 1] <= '9')) or
          s[n] in ')'):  # '0' のつぎは数字はこない
      v = vv - set('0123456789')
    elif depth == 1:  # 最後の一個は数字か閉括弧
      v = vv - set('+-/*(')
    else:
      v = vv
    if algo == 'bara':  # バラバラであれ
      v = v - set(s)

    v = v - set(blow[n + 1])

    if '(' in s:
      v = v - set('(')
      if ')' in s:
        v = v - set(')')
    else:
      v = v - set(')')
    if op <= 0:
      v = v - set('+-*/')

    for a in v:
      o = op - 1 if a in '+-*/' else op
      self._solve(depth - 1, o, vv, hit, blow, pp, s + a, algo)

  def solve(self, algo: str):
    self.cost = [0] * 10
    self.costs = [[0] * 10] * self.depth
    self.cand = []
    vv = set('1234567890+-/*()') - self.out
    hit = ''.join(self.hit)
    blow = self.blow
    print(f'hit={hit}')
    print(f'blow={blow}')
    print(f'cand={vv}')

    if algo in ['bara', 'all']:
      pass
    elif len(vv) == 16 or len(set(hit)) == 1:   # 0ヒット
      algo = 'bara'
    elif hit == '________' and len(vv) >= 14:
      algo = 'bara'
    else:
      algo = 'all'
    if self.depth < 8:
      vv = vv - set('()')

    # 答えに含まれることが確定している数字や演算子
    pp = set()
    for i in range(len(blow)):
      blow[i] = set(blow[i])
      pp = pp | blow[i]
    pp = pp | set(hit) - set('_')

    for op in range(self.op, 0, -1):
      self._solve(self.depth, op, vv, hit, blow, pp, '', algo)
      if len(self.cand) > 0:
        break
    self.cmp_cost()
    self.cand.sort(key=lambda x: self.weight(x))
    for p in self.cand:
      print(f'{p}, {self.weight(p)}')

  def cmp_cost(self):
    self._init_costs()
    for c in self.cand:
      for j, s in enumerate("0123456789"):
        if s in c:
          self.cost[j] += 1
      for i, ci in enumerate(c):
        if '0' <= ci <= '9':
          self.costs[i][ord(ci) - ord('0')] += 1

  def weight(self, x):
    """

    >>> w = Mathler(8, 11)
    >>> w.cand.append('4*5+2')
    >>> w.cand.append('3*1+9')
    >>> w.cand.append('9*0-3')
    >>> w.weight('3*5+2')[:3]
    (5, 2, 9)
    >>> w.weight('3*5-2')[:3]
    (5, 2, 7)
    >>> w.weight('10/2+6')[2]
    7
    >>> w.weight('10*2+6')[2]
    9
    >>> w.cmp_cost()
    >>> print(w.cand, file=sys.stderr)
    >>> print(w.costs, file=sys.stderr)
    >>> w.weight('7*8-6')[:5]
    (5, 2, 7, 9, 0)
    >>> w.weight('3*8-6')[:5]
    (5, 2, 7, 9, 1)
    """
    xx = set(x)
    w0 = len(xx - set(')'))  # 文字種別数
    w1 = len(xx & set("*+/-("))  # 記号種別数
    w2 = 0  # 記号の優先度
    for i, op in enumerate("*+/-"):
      if op in x:
        w2 += 5 - i
    w3 = 0
    for s in xx and set('0123456789'):  # 数字の優先度
      w3 += self.cost[ord(s) - ord('0')]

    w4 = 0
    for i, s in enumerate(x):
      w4 += self.costs[i][ord(s) - ord('0')]
    return (w0, w1, w2, w3, w4)


def main():
  import argparse

  parser = argparse.ArgumentParser(description='')
  parser.add_argument('args', nargs='*', help='hit=o, blow=x, out=_|-')
  parser.add_argument('-k', choices=[8, 6, 5], default=8, type=int,
                      help="# of squares: hard=8, normal=6, easy=5")
  parser.add_argument('-v', action='store_true')
  parser.add_argument('-a', required=True, type=int)
  parser.add_argument('-s', choices=['bara', 'all'])
  parser.add_argument('-t', action='store_true')
  args = parser.parse_args()

  depth = args.k
  ans = args.a
  w = Mathler(depth, ans)

  if args.t:
    doctest.testmod()
    return

  if len(args.args) % 2 != 0:
    print('usage....', file=sys.stderr)
    return 2

  for i in range(0, len(args.args), 2):
    w.add(args.args[i], args.args[i + 1])

  w.solve(args.s)
  print("finished")


if __name__ == '__main__':
  main()


# vim:set et ts=2 sts=2 sw=2 tw=80:
