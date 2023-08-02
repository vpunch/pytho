import sys

print('foo')

#print('path', sys.path)
#print('modules', list(sys.modules.keys())[-2:])
import main


# from <module_name> import * никогда не использовать, это мешает линтеру

print('bar')
