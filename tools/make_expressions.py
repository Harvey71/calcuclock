import random
import re

def random_expression():
    # 5 random digits
    arr = [str(random.randint(0, 9)) for _ in range(5)]
    # place one or two operators
    for _ in range(random.randint(1, 2)):
        arr[random.randint(0, 4)] = random.choice(['+', '*', '-', '/'])
    return ''.join(arr)


expressions = {
    num: [] for num in range(0,60)
}
target_len = 200
cnt = 0
while True:
    cnt += 1
    if cnt % 10000 == 0:
        num = 0
        for arr in expressions.values():
            num += len(arr)
        print(f'{cnt} steps: {num} expressions')
        if num >= 60 * target_len:
            break
    expr = random_expression()
    # ignore expression with two operators in a row
    if re.search('\D\D', expr):
        continue
    # ignore expressions beginning with operator other than minus
    if not re.search('^[-\d]', expr):
        continue
    # ignore leading zeros
    if re.search('($|\D)0\d', expr):
        continue
    # ignore trivial operations
    if re.search('(^|\D)(0+|1)($|\D)', expr):
        continue
    # ignore faulty expressions
    try:
        result = eval(expr)
    except:
        continue
    # ignore results with fractional part
    if result % 1 != 0:
        continue
    result = int(result)
    # only take results in desired range
    if 0 <= result <= 59:
        if len(expressions[result]) < target_len:
            expressions[result].append(expr)

with open('../code/expressions.txt', 'w') as f:
    for result in range(60):
        f.write(','.join(expressions[result]) + '\n');

