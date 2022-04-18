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
      print([s, len(u)], flush=True)
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


def check_arg(args) -> bool:
  if len(args.args) % 2 != 0:
    print('# of args should be even', file=sys.stderr)
    return False
  for i, s in enumerate(args.args):
    if len(s) != args.k:
      print(f'len(args[{i}]) != {args.k}: {s}', file=sys.stderr)
      return False
    if i % 2 == 0:
      # 文法誤り
      try:
        if parse(s) != args.a:
          print(f'{s} != {args.a}: {i}th arg', file=sys.stderr)
          return False
      except Exception:
        print(f'{i}th arg is invalid: {s}', file=sys.stderr)
        return False
    elif len(set(s) - set('ox_-')) != 0:
      print(f'{i}th arg is invalid: {s}', file=sys.stderr)
      return False
  return True


def main():
  import argparse

  parser = argparse.ArgumentParser(description='')
  parser.add_argument('args', nargs='*', help='hit=o, blow=x, out=_|-')
  parser.add_argument('-k', choices=[8, 6, 5], default=8, type=int,
                      help="# of squares: hard=8, normal=6, easy=5")
  parser.add_argument('-v', action='store_true')
  parser.add_argument('-a', required=True, type=int)
  args = parser.parse_args()

  if not check_arg(args):
    doctest.testmod()
    print('usage....', file=sys.stderr)
    return 2

  ans = args.a
  depth = args.k
  op = {8: 3, 6: 2, 5: 1}[depth]
  out = set()  # 灰
  # 緑   12345678
  hit = ['_'] * depth
  blow = [''] * depth  # 黄色
  for i in range(0, len(args.args), 2):
    for j in range(depth):
      s = args.args[i + 0][j]
      t = args.args[i + 1][j]
      if t == 'o':  # hit
        assert hit[j] == '_' or hit[j] == s
        hit[j] = s
      elif t == 'x':  # blow
        blow[j] += s
      else:
        out.add(s)
  vv = set('1234567890+-/*()') - out
  hit = ''.join(hit)
  if args.v:
    print(f'hit={hit}')
    print(f'blow={blow}')
    print(f'vv={vv}')

  solve(depth, op, vv, ans, hit, blow, '')
  print("finished")


if __name__ == '__main__':
  main()


# vim:set et ts=2 sts=2 sw=2 tw=80:
