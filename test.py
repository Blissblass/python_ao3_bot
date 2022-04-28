import os

def test():
  if os.environ.get('ENV') == 'DEV':
    print("DEV LOL")
  else:
    print("NOT DEV LOL")

test()