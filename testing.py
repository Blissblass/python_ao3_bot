import re 

def re_test():
  return int("".join(re.findall('\d', '(1356245,)')))

print(re_test())  