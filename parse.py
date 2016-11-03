class Vxml:
    version=None
    internalTags=[]
    text=''

class Form:
    iD=None
    internalTags=[]
    text=''

class Field:
    name=None
    internalTags=[]
    text=''

class Var:
    expr=None
    internalTags=[]

def FindClass(tag, args, tags, text):
    c=None
    if 'vxml' in tag:
        c=Vxml()
        if 'version' in args:
    
            c.version=args['version']
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
    #-----------------
    if 'var' in tag:
        c=Var()
        if 'expr' in args:
            c.expr=args['expr']
    
    #tagClasses=[]
    #for tag in tags:
    #        tagClass=FindClass(tag,{},[])
    #        tagClasses.append(tagClass)
    c.internalTags=tags
    c.text=text

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

#некоторые теги <tag></tag>
tagsRepeat=['vxml','form','field']
#а некоторые <tag/>
tagsNoRepeat=['var']

def CreateTree(words):
    tags=[]

    #текст
    if words[0][0]!='<':
        return words
    
    while words!=[]:
        internalTags=[]
        nameTag=DelUnChar(words[0])
        del words[0]

        #аргументы тега (поля класса)
        args={}
        try:
            while '=' in words[0]:
                arg=words[0].split('=')
                args[DelUnChar(arg[0])]=DelUnChar(arg[1])
                del words[0]
        except:
            args={}
        
        #тег заканчивается </tag>
        #поэтому содержит не только аргументы, но и внутренние теги,
        #а также какой-нибудь текст (возможно)
        if nameTag in tagsRepeat:
            
            contentOFtag=[]
            #ищем конец тега
            while ((nameTag in words[0])==False):
                contentOFtag.append(words[0])
                del words[0]
                
            #тег закончился
            #внутренние теги в рекурсию
            #и удалить закрывающийся тег
            del words[0]
            internalTags=CreateTree(contentOFtag)
            
        #тег заканчивается />
        #содержит только аргументы
        #if nameTag in tagsNoRepeat:
            #internalTags=[]
        
        if (len(internalTags)>0) and (type(internalTags[0])!=str):
            tags.append(FindClass(nameTag,args,internalTags,''))
        else:
            tags.append(FindClass(nameTag,args,[],internalTags))
            

    return tags







           

#Возвращается содержание(аргументы и вложенные теги) одного тега
#и строчка с концом
#из подаваемого тега берется первый попавшийся тег
#def ContentOfTag(text):
       



  



    
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


#a=CreateTree(Split())





