from parse import parse
from tagslib import *

print('*** VoiceXML 2.1 to Python 2.7 Translator ***')
print('Input: \'vxml-file path \' \'py-file path\'')
# inputed_line = raw_input('> ')
# paths = inputed_line.split(' ')
paths = ['test.vxml', '1.py']

classes = []
init_lines = []

def describeTag(three, outfile, ancestor=None, lvl=0):
    for t in three:
        tag = 'tags[%s]' % lvl
        init_lines.append('tags.append(' + t.description + ')\n')

        if not (ancestor is None):
            init_lines.append(ancestor + '.internal_tags.append(' + tag + ')' + '\n')
        lvl += 1
        if isinstance(t, Scope):
            describeTag(t.internal_tags, outfile, tag, lvl)

        t_isinstance = False
        for cls in classes:
            if (isinstance(t, cls.__class__)): t_isinstance = True
        if t_isinstance == False:
            classes.append(t)



try:
    three = parse(paths[0])
    dir(three[0])
    outfile = open(paths[1], 'w')

    outfile.write('#from base import *' + '\n')
    outfile.write('from tagslib import *' + '\n')
    outfile.write('\n')
    describeTag(three, outfile)

    classes.reverse()
    descriptions = []
    for cls in classes:
        descriptions.append(cls.describe())


    outfile.write(''.join(descriptions))
    outfile.write('tags = []\n')
    outfile.write(''.join(init_lines))

    outfile.close()

    print(classes)

except IOError:
    print('file not exist')
