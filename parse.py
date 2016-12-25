# -*- coding: utf-8 -*-
from tagslib import *


def find_class(tag, args, tags, text):
    c = None

    if 'vxml' in tag:

        version = args['version'] if ('version' in args) else None
        xml_base = args['xml:base'] if ('xml:base' in args) else  None
        application = args['application'] if ('application' in args) else None
        xml_lang = args['xml:lang'] if ('xml:lang' in args) else None
        xmlns = xmlns = args['xmlns'] if ('xmlns' in args) else None

        c = Vxml(version, xml_base, application, xml_lang, xmlns, tags)
    # -----------------
    if 'form' in tag:
        Id = args['id'] if ('id' in args) else None
        scope = args['scope'] if ('scope' in args) else None

        c = Form(Id, scope, tags)
    # -----------------
    if 'prompt' in tag:
        bargein = args['bargein'] if ('bargein' in args) else None
        bargeintype = args['bargeintype'] if ('bargeintype' in args) else None
        cond = args['cond'] if ('cond' in args) else None
        count = args['count'] if ('count' in args) else None
        timeout = args['timeout'] if ('timeout' in args) else None
        xml_lang = args['xml_lang'] if ('xml_lang' in args) else None

        c =Prompt(bargein, bargeintype, cond, count, timeout, xml_lang, tags, text)
    # -----------------
    if 'block' in tag:
        name = args['name'] if ('name' in args) else None
        expr = args['expr'] if ('expr' in args) else None
        cond = args['cond'] if ('cond' in args) else None

        c = Block(name, expr, cond, tags)
    # -----------------

    return c


# Вызов парсера
def parse(path):
    text = read_file(path)
    split_text = split(text)
    return create_tree(split_text)


def split(text):
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


def create_tree(words):
    tags = []

    # текст
    if words[0][0] != '<':
        return words

    while words != []:
        internalTags = []
        nameTag = del_un_char(words[0])
        del words[0]

        # аргументы тега (поля класса)
        args = {}
        try:
            while '=' in words[0]:
                arg = words[0].split('=')
                args[del_un_char(arg[0])] = del_un_char(arg[1])
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
            internalTags = create_tree(contentOFtag)

        if (len(internalTags) > 0) and (type(internalTags[0]) != str):
            tags.append(find_class(nameTag, args, internalTags, []))
        else:
            tags.append(find_class(nameTag, args, [], internalTags))
    return tags


# Удаление ненужных символов из строки
def del_un_char(s):
    unChar = '<>"'
    newStr = []
    for c in s:
        if ((c not in unChar) or ((c == '/') and (newStr[len(newStr) - 1] != '<'))):
            newStr.append(c)
    return ''.join(newStr)


def read_file(path):
    f = open(path, 'r')
    lines = []
    for line in f:
        lines.append(line)
    f.close()
    return ' '.join(lines)
