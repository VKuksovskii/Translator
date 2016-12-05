# -*- coding: utf-8 -*-
from tags import *


def FindClass(tag, args, tags, text):
    c = None
    '''
    print(tag)
    print(args)
    print(tags)
    print(text)
    print('----')
    '''
    if 'vxml' in tag:

        version = None
        xml_base = None
        application = None
        xml_lang = None
        xmlns = None

        if 'version' in args:
            version = args['version']
            if (version != "2.0" and version != "2.1"):
                raise Exception("bad vxml version")

        if 'xml_base' in args:
            xml_base = args['xml:base']

        if 'application' in args:
            application = args['application']

        if 'xml_lang' in args:
            xml_lang = "en-Us" if (args['xml:lang'] is None) else args['xml:lang']

        if 'xmlns' in args:
            xmlns = args['xmlns']
            if (xmlns is None):
                raise Exception("bad xmlns")

        c = Vxml(version, xml_base, application, xml_lang, xmlns)
        # -----------------
    if 'form' in tag:
        Id = None
        scope = None
        if 'id' in args:
            Id = args['id']
        else:
            # formCng нужен для генерации id формы по нему, реализован как статическая переменная
            try:
                FindClass.formCnt += 1
            except:
                FindClass.formCnt = 0
            Id = FindClass.formCnt
        if 'scope' in args:
            scope = args['scope']
            if (scope != None):
                if (scope != "dialog" and scope != "document"):
                    raise Exception("bad scope")
            else:
                scope = "dialog"

        c = Form(Id, scope)
    # -----------------
    if 'prompt' in tag:
        bargein = None
        bargeintype = None
        cond = None
        count = None
        timeout = None
        xml_lang = None
        if 'bargein' in args:
            bargein = args['bargein']
        if 'bargeintype' in args:
            bargeintype = args['bargeintype']
        if 'cond' in args:
            cond = args['cond']
        if 'count' in args:
            count = args['count']
        if 'timeout' in args:
            bargein = args['timeout']
        if 'xml:lang' in args:
            xml_lang = args['xml:lang']

        bargein = True if bargein is None else bargein
        bargeintype = True if bargeintype is None else bargeintype
        cond = True if cond is None else cond
        count = 1 if count is None else count
        timeout = 5 if timeout is None else timeout
        xml_lang = xml_lang

        c = Prompt(bargein, bargeintype, cond, count, timeout,
                   xml_lang)
    # -----------------
    if 'block' in tag:
        name = None
        expr = None
        cond = None
        if 'name' in args:
            name = args['name']
        if 'expr' in args:
            expr = args['expr']
        if 'cond' in args:
            cond = args['cond']

        if (cond == None): cond = True

        c = Block(name, expr, cond)
    # -----------------

    c.internalTags = tags
    # [(vxml, [form, [block, [promt]]])]
    c.text = text

    return c


# Вызов парсера
def Parser(path):
    text = ReadFile(path)
    splitText = Split(text)
    return CreateTree(splitText)


def Split(text):
    s = []
    word = ""
    unnecessaryChar = ['\n', '\t']
    i = 0

    # TODO - запилить проверку
    # удаление  <?xml>
    while text[i] != '<' or len(text) < i:
        i += 1

    if ((text[i] == '<') and (text[i + 1] == '?')):
        while text[i] != '>':
            i += 1

    text = text[i + 1:]

    for i, l in enumerate(text):
        if (l in unnecessaryChar) == False:
            if l == ' ':
                if (word != "") and (i > 0) and (i < len(text) - 1) and (text[i - 1] != '=') and (text[i + 1] != '='):
                    s.append(word)
                    word = ""
            else:
                word += l
    s.append(word)
    # word=""
    return s


# TODO - убрать этот ужас
# некоторые теги <tag></tag>
tagsRepeat = ['vxml', 'form', 'field', 'block', 'prompt']
# а некоторые <tag/>
tagsNoRepeat = ['var']


def CreateTree(words):
    tags = []

    # текст
    if words[0][0] != '<':
        return words

    while words != []:
        internalTags = []
        nameTag = DelUnChar(words[0])
        del words[0]

        # аргументы тега (поля класса)
        args = {}
        try:
            while '=' in words[0]:
                arg = words[0].split('=')
                args[DelUnChar(arg[0])] = DelUnChar(arg[1])
                del words[0]
        except:
            args = {}

        # тег заканчивается </tag>
        # поэтому содержит не только аргументы, но и внутренние теги,
        # а также какой-нибудь текст (возможно)

        if nameTag in tagsRepeat:

            contentOFtag = []

            # ищем конец тега
            while ((nameTag in words[0]) == False):
                contentOFtag.append(words[0])
                del words[0]

            # тег закончился
            # внутренние теги в рекурсию
            # и удалить закрывающийся тег

            del words[0]
            internalTags = CreateTree(contentOFtag)

        if (len(internalTags) > 0) and (type(internalTags[0]) != str):
            tags.append(FindClass(nameTag, args, internalTags, []))
        else:
            tags.append(FindClass(nameTag, args, [], internalTags))

    return tags


# Удаление ненужных символов из строки
def DelUnChar(s):
    unChar = '<>"'
    newStr = ''
    for c in s:
        if (((c in unChar) == False) or ((c == '/') and (newStr[len(newStr) - 1] != '<'))):
            newStr += c

    return newStr


def ReadFile(path):
    f = open(path, 'r')
    lines = []
    for line in f:
        lines.append(line)
    f.close()
    text = ""
    for l in lines:
        text += ' ' + l
    return text
