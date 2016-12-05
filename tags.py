# -*- coding: utf-8 -*-
import threading

tab = '    '


def makeTabs(strings, level):
    text = ''
    tabs = ''
    for i in range(level):
        tabs += tab
    for s in strings:
        text += tabs + s + '\n'
    return text


def getTags(three, tagType, count = 0):
    tags = []
    for t in three:
        if isinstance(t, tagType):
            # try for tags, who haven't internal tags
            try:
                tags.extend(getTags(t.internalTags, tagType, count + 1))
            except:
                pass

            if isinstance(t, Var):
                tags.append((t.name, t.expr))
            elif isinstance(t, FormItem):
                if t.name is None:
                    tags.append('%s_%i' % ( t.__class__.__name__, count))
                else:
                    tags.append(t.name)
            elif isinstance(t, Script):
                tags.append(t.text)

        return tags


class FormItem:
    def __init__(self, name, expr, cond=True):
        self.name = name
        self.expr = expr
        self.cond = cond
        self.variable = None


class InputItem(FormItem):
    def __init__(self, name, expr, cond):
        FormItem.__init__(self, name, expr, cond)


class ControlItem(FormItem):
    def __init__(self, name, expr, cond):
        FormItem.__init__(self, name, expr, cond)


class Vxml:
    # may contain form, menu, meta, var, link
    # < catch > < error > < form > < help > < link > < menu > < meta > < noinput > < nomatch > < property > < script >
    internalTags = []

    def __init__(self, version, xml_base, application, xml_lang, xmlns):
        """
        application = "CDATA"
        version = "(2.0|2.1)"
        xml:base = "CDATA"
        xml:lang = "NMTOKEN"
        xmlns = "http://www.w3.org/2001/vxml"
        """
        if (version != "2.0" and version != "2.1"):
            raise Exception("bad vxml version")

        if (xmlns is None):
            raise Exception("bad xmlns")

        self.version = version
        self.xmlns = xmlns
        self.xml_base = xml_base
        self.xml_lang = "en-Us" if (xml_lang is None) else xml_lang
        self.application = application

    def describe(self):
        formCount = False
        text = ''
        for t in self.internalTags:
            if not ((t is Form) or (t is Menu)) or formCount is False:
                text += t.describe(1)
            if t is Form or t is Menu:
                formCount = True

        return text


class Form:
    # may contain field, record, transfer, object, subdialog, initial, block, grammar, var, catch,
    # < block > < catch > < error > < field > < filled > < grammar > < help > < initial > < link > < noinput > < nomatch > < property > < record > < script > < subdialog > < transfer >
    internalTags = []

    def __init__(self, Id, scope):
        if (scope != None):
            if (scope != "dialog" and scope != "document"):
                raise Exception("bad scope")
            else:
                self.scope = scope
        else:
            self.scope = "dialog"
        self.Id = Id

    def describe(self, level):
        text = []

        #outfile.write('\n')

        #outfile.write('if ' + '\n')

        text.append('variables = {}' + '\n')

        for fi in getTags(self.internalTags, FormItem):
            text.append('variables[%s] = None\n' % fi)

        for v in getTags(self.internalTags, Var):
            text.append('variables[%s] = %s\n' % (v[0], v[1]))

        for s in getTags(self.internalTags, Script):
            text.append('variables[%s] = %s\n' % (s[0], s[1]))

        text.append('var next = None\n')

        text.append('while true:\n')
        text.append('    if not (next is None):\n')






        text = makeTabs(text,level)

        level += 1
        formCount = False

        for t in self.internalTags:
            if not ((t is Form) or (t is Menu)) or formCount is False:
                text += t.describe(level+1)
            if t is Form or t is Menu:
                formCount = True

        return text


class Subdialog(InputItem):
    # may contain filled
    internalTags = []

    def __init__(self, name, expr, cond, namelist, src, srcexpr, method, enctype, fetchaudio, fetchhint, fetchtimeout,
                 maxage, maxstale):
        InputItem.__init__(self, name, expr, cond)
        self.namelist = namelist
        self.src = src
        self.srcexpr = srcexpr
        self.method = method
        self.enctype = enctype
        self.fetchaudio = fetchaudio
        self.fetchhint = fetchhint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale


class Field(InputItem):
    # may contain grammar, prompt,filled, catch, help, option
    internalTags = []

    def __init__(self, name, expr, cond, ftype, slot, modal):
        def __init__(self, name, expr, cond):
            InputItem.__init__(self, name, expr, cond)

        self.ftype = ftype
        self.slot = slot
        self.modal = modal


class Menu:
    # may contain Choice, prompt, enumerate, noinput
    internalTags = []

    def __init__(self, id, dtmf, acccept):
        self.id = id
        self.dtmf = dtmf
        self.acccept = acccept


class Choice:
    # may contain grammar
    internalTags = []

    def __init__(self, dtmf, acccept, next, expr, event, eventexpr, massage, messageexpr, fetchaudio, fetchhint,
                 fetchtimeout, maxage, maxstale):
        self.dtmf = dtmf
        self.acccept = acccept
        self.next = next
        self.expr = expr
        self.event = event
        self.eventexpr = eventexpr
        self.massage = massage
        self.messageexpr = messageexpr
        self.fetchaudio = fetchaudio
        self.fetchhint = fetchhint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale


class Catch:
    # may contain reprompt, goto, submit, if
    internalTags = []


class Goto:
    pass


class Prompt:
    # may contain audio, enumerate
    # < audio > <break > < emphasis > < enumerate > < foreach > < mark > < paragraph > < phoneme > < prosody > < say -as > < sentence > < value >
    internalTags = []

    def __init__(self, bargein, bargeintype, cond, count, timeout, xml_lang):
        """
        bargein = "(true|false)"
        bargeintype = "(speech|hotword)"
        cond = "CDATA"
        count = "CDATA"
        timeout = "CDATA"
        xml_lang = "NMTOKEN"
        """
        self.bargein = True if bargein is None else bargein
        self.bargeintype = True if bargeintype is None else bargeintype
        self.cond = True if cond is None else cond
        self.count = 1 if count is None else count
        self.timeout = 5 if timeout is None else timeout
        self.xml_lang = xml_lang

    def describe(self, level):
        return makeTabs(['# bargein ???' \
                            , '# bargeintype ???' \
                            , '# xml:lang - т.к. один документ, то берется из него же' \
                            , '# cond нужно преобразовать в условие' \
                            , 'if cond is True and self.form.count == self.count:' \
                            , tab + 'naulib.sayText(%s)' % self.text], level)


class Reprompt:
    pass


class Initial(ControlItem):
    # may contain prompt, help, noinput
    internalTags = []

    def __init__(self, name, expr, cond):
        ControlItem.__init__(self, name, expr, cond)
        self.promptCnt = 1


class Noinput:
    # may contain assign
    internalTags = []


class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Filled:
    # may contain if, clear, assign, return, var
    internalTags = []


class If:
    # may contain assign, exit, else, clear, throw, elseif, submit
    internalTags = []


class Block(ControlItem):
    # may contain submit, value, goto
    # < audio > < assign > < clear > < data > < disconnect > < enumerate > < exit > < foreach > < goto > < if > < log > < prompt > < reprompt > <
    # return > < script > < submit > < throw > < value > < var >
    internalTags = []

    def __init__(self, name, expr, cond):
        """
           name="string"
           expr="ECMAScript_Expression"
           cond="ECMAScript_Expression"
        """
        if (cond == None): cond = True
        ControlItem.__init__(self, name, expr, cond)

    def describe(self, level):
        result = ''
        for t in self.internalTags:
            result += t.describe(level + 1)


        return makeTabs(['# var %s = %s' % (self.name, self.expr) \
                            , '# expr нужно преобразовать в условие' \
                            , '# cond нужно преобразовать в условие' \
                            , 'if cond is True'], level) + result


class Link:
    # may contain grammar
    internalTags = []


class Grammar:
    # may contain rule
    internalTags = []


class Rule:
    # may contain one-of
    internalTags = []


class Oneof:
    # may contain item
    internalTags = []


class Item:
    # may contain item
    internalTags = []


class Enumerate:
    # may contain value
    internalTags = []


class Option:
    def __init__(self, dtmf, accept, value):
        self.dtmf = dtmf
        self.accept = accept
        self.value = value


class Transfer(InputItem):
    def __init__(self, name, expr, cond, dest, destexpr, bridge, connecttimeout, maxtime, transferaudio, aai, aaiexpr):
        InputItem.__init__(self, name, expr, cond)
        self.dest = dest
        self.destexpr = destexpr
        self.bridge = bridge
        self.connecttimeout = connecttimeout
        self.maxtime = maxtime
        self.transferaudio = transferaudio
        self.aai = aai
        self.aaiexpr = aaiexpr


class Record(InputItem):
    # has grammar, prompt and catch elements. It may also have <filled> actions.
    internalTags = []

    def __init__(self, name, expr, cond, modal, beep, maxtime, finalsilence, dtmfterm, type):
        InputItem.__init__(self, name, expr, cond)
        self.cond = cond
        self.modal = modal
        self.beep = beep
        self.maxtime = maxtime
        self.finalsilence = finalsilence
        self.dtmfterm = dtmfterm
        self.type = type

        def duration():
            pass

        def size():
            pass

        def termchar():
            pass

        def maxtime():
            pass


class Object(InputItem):
    # has prompts and catch elements. It may also have <filled> actions.
    internalTags = []

    def __init__(self, name, expr, cond, classid, codebase, codetype, data, type, archive, fetchhint, fetchtimeout,
                 maxage, maxstale):
        InputItem.__init__(self, name, expr, cond)
        self.classid = classid
        self.codebase = codebase
        self.codetype = codetype
        self.data = data
        self.archive = archive
        self.fetchhint = fetchhint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale


class Var:
    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr


class Script:
    def __init__(self, src, charset, fetchhint, fetchtimeout, maxage, maxstale, text):
        self.src = src
        self.charset = charset
        self.fetchhint = fetchhint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale
        self.text = text
