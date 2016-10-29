print ('*** VoiceXML 2.1 to Python 2.7 Translator ***')
print ('Input: \'vxml-file path \' \'py-file path\'')

inputedLine = raw_input('> ')

paths = inputedLine.split(' ')

vxmlFile = open(paths[0], 'r')

#tags = parse(vxmlFile)

#tags = Form()

#print (tags)