#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import doctest


def dprint(s):
  """for debug"""
  if False:
    print(s, file=sys.stderr)
  pass


def lex(s):
  """lexer

  >>> lex("1 3 45")
  [1, 3, 45]
  >>> lex("1 +- )3 4")
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


def _factor(tokens, i):
  dprint(["_factor", i, tokens[i]])
  if isinstance(tokens[i], int):
    return tokens[i], i + 1
  if tokens[i] == '(':
    val, i = _expr(tokens, i + 1)
    if tokens[i] != ')':
      raise Exception(f'expected ")", {tokens[i+1]},{i+1}')
    return val, i + 1
  raise Exception('expected "(", {tokens[1]},{i}')


def _term(tokens, i):
  dprint(["_term", i, tokens[i]])
  val, i = _factor(tokens, i)
  while i < len(tokens) and tokens[i] in ['*', '/']:
    op = tokens[i]
    v, i = _factor(tokens, i + 1)
    if op == '*':
      val *= v
    elif v == 0:
      raise Exception('zero division')
    elif isinstance(val, int) and isinstance(v, int) and val % v == 0:
      val //= v
    else:
      val /= v
  return val, i


def _expr(tokens, i):
  dprint(["_expr", i, tokens[i]])
  val, i = _term(tokens, i)
  while i < len(tokens) and tokens[i] in ['+', '-']:
    op = tokens[i]
    v, i = _term(tokens, i + 1)
    if op == '+':
      val += v
    else:
      val -= v
  return val, i


def parse(s):
  """

  >>> parse("3+4+5")
  12
  >>> parse("3-4+5")
  4
  >>> parse("5*8")
  40
  >>> parse("3+8/2")
  7
  >>> try: print(parse("83-3(/38"))
  ... except: print("except")
  except
  >>> try: print(parse("(99()*98"))
  ... except: print("except")
  except
  >>> try: print(parse("(9))*898"))
  ... except: print("except")
  except
  >>> parse("9*998/9")
  998
  """
  v = lex(s)
  dprint(["parse", s, v])
  val, i = _expr(v, 0)
  if i != len(v):
    raise Exception('invalid')
  return val


def _solve0(ans, pp, s):
  if pp & set(s) != pp:
    return
  try:
    v = parse(s)
    if -0.001 < v - ans < 0.001:
      u = set(s)
      print([s, len(u)])
  except Exception:
    pass
  return


def _solve(depth, op, vv, ans, hit, blow, pp, s, algo):
  if depth == 0:
    return _solve0(ans, pp, s)

  n = len(s) - 1

  # 計算量削減のため不要なものは取り除く
  if hit[n + 1] != '_':
    v = set(hit[n + 1])
  elif n == -1 or s[n] in '+-/*(':  # 1文字目は数字か開括弧
    v = vv - set('+-/*)')
  elif s[n] == '0' or s[n] in ')':  # '0' のつぎは数字はこない
    v = vv - set('0123456789')
  elif depth == 1:  # 最後の一個は数字か閉じ括弧
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
    _solve(depth - 1, o, vv, ans, hit, blow, pp, s + a, algo)


def solve(depth, op, vv, ans, hit, blow, s):
  if len(vv) == 16 or hit == '________':
    algo = 'bara'
  elif depth == 8 and hit == '________' and len(vv) >= 14:
    algo = 'bara'
  else:
    algo = 'all'
  if depth < 8:
    vv = vv - set('()')

  pp = set()
  for i in range(len(blow)):
    blow[i] = set(blow[i])
    pp = pp | blow[i]
  pp = pp | set(hit) - set('_')

  return _solve(depth, op, vv, ans, hit, blow, pp, s, algo)


doctest.testmod()

ans = 228
depth = 8  # high=8, normal=6, easy=5
op = {8: 3, 6: 2, 5: 1}[depth]

out = set('14256780')   # 手入力 グレーなやつ
# 緑   12345678
hit = '_______8'

blow = [  # 黄色
    '',  # 1
    '',  # 2
    '3*',  # 3
    '*',  # 4
    '-',  # 5
    '-3',  # 6
    '',  # 7
    '',  # 8
]

vv = set('1234567890+-/*()') - out
solve(depth, op, vv, ans, hit, blow, '')
print("finished")


# vim:set et ts=2 sts=2 sw=2 tw=80:
