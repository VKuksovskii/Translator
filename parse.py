class Vxml:
    version=None
    tags=[]

class Form:
    iD=None
    tags=[]

class Field:
    name=None
    tags=[]

def FindClass(tag, args, tags):
    c=None
    if 'vxml' in tag:
        c=Vxml()
        if 'version' in args:
            c.version=args['version']
            c.tags=tags
    #-----------------
    if 'form' in tag:
        c=Form()
        if 'id' in args:
            c.iD=args['id']
    #-----------------
    if 'field' in tag:
        c=Field()
        if 'name' in args:
            c.name=args['name']

    
    #tagClasses=[]
    #for tag in tags:
    #        tagClass=FindClass(tag,{},[])
    #        tagClasses.append(tagClass)
    

    return c
    

def Split():
    s=[]
    word=""
    unnecessaryChar=['\n','\t']
    text=ReadFile()
    #for line in text:
    for i, l in enumerate(text):
        if (l in unnecessaryChar)==False:
            if l ==' ':
                if (word!="") and (i>0) and (i<len(text)-1) and (text[i-1]!='=') and (text[i+1]!='='):
                    s.append(word)
                    word=""
            else:
                word+=l
    s.append(word)
        #word=""
    return s

def CreateTree():
    tag=''
    args={}
    tags=[]
    text=Split()
    listOneTag=[]
    
    for i, word in enumerate(text):
        if (word[0]=='<'):
            listOneTag=ListOneTag(text,i)
            classTag=CreateTagClass(listOneTag, DelUnChar(word))
            tags.append(classTag)


def CreateTagClass(listTag, nameTag):
    args={}
    tags=[]
    #del listTag[0]
    i=0
    while '=' in listTag[i]:
        arg=listTag[i].split('=')
        args[arg[0]]=arg[1]
        i+=1
    for t in listTag:
        if ('<' in t) and ('/' in t)==False:
            tag=FindClass(t,{},[])
            tags.append(tag)
    tag=FindClass(nameTag, args, tags)
    return tag

  

def ListOneTag(listD, num):
    l=[]
    stopTag='/'+DelUnChar(listD[num])
    tag=DelUnChar(listD[num])
    #for i, a in enumerate(listD):
    #    if (i>=num) and ((stopTag in a)==False):
    #        l.append(a)
    i=num+1
    while (tag in listD[i])==False:
        l.append(listD[i])
        i+=1
    return l


    
#ФУНКЦИЯ ДЛЯ УБИРАНИЯ НЕНУЖНЫХ СИМВОЛОВ
def DelUnChar(s):
    unChar='</>"'
    newStr=''
    for c in s:
        if (c in unChar)==False:
            newStr+=c
    return newStr


def ReadFile():
    f = open('код_текст.txt', 'r')
    lines = []
    for line in f:
        lines.append(line)
    f.close()
    text=""
    for l in lines:
        text+=' '+l
    return text








