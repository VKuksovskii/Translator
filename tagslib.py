# -*- coding: utf-8 -*-

tab = '    '


class Scope:
    def __init__(self, internal_tags):
        self.internal_tags = internal_tags


def makeTabs(strings, level):
    text = ''
    tabs = ''
    for i in range(level):
        tabs += tab
    for s in strings:
        text += tabs + s + '\n'
    return text


def getTags(three, tagType, count=0):
    tags = []
    for t in three:
        if isinstance(t, tagType):
            if isinstance(t, Scope):
                tags.extend(getTags(t.internal_tags, tagType, count + 1))

            if isinstance(t, Var):
                tags.append((t.name, t.expr))
            elif isinstance(t, FormItem):
                if t.name is None:
                    tags.append('%s_%i' % (t.__class__.__name__, count))
                else:
                    tags.append(t.name)
            elif isinstance(t, Script):
                tags.append(t.text)

        return tags


class FormItem:
    def __init__(self, name, expr, cond=True):
        self.name = name
        if (name is None):
            # formCnt нужен для генерации name формы по нему, реализован как статическая переменная
            try:
                FormItem.formCnt += 1
            except:
                FormItem.formCnt = 0
                self.name = FormItem.formCnt
        self.expr = expr
        self.cond = cond
        self.variable = None


class InputItem(FormItem):
    def __init__(self, name, expr, cond):
        FormItem.__init__(self, name, expr, cond)
        self.prompt_counter = 1


class ControlItem(FormItem):
    def __init__(self, name, expr, cond):
        FormItem.__init__(self, name, expr, cond)


class Vxml(Scope):
    # may contain form, menu, meta, var, link
    # < catch > < error > < form > < help > < link > < menu > < meta > < noinput > < nomatch > < property > < script >

    def __init__(self, version, xml_base, application, xml_lang, xmlns, internal_tags):
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

        Scope.__init__(self, internal_tags)

        self.description = 'Vxml(version:%s, xml_base:%s, application:%s, xml_lang:%s, xmlns:%s)' % (
            version.__repr__(), xml_base.__repr__(), application.__repr__(), xml_lang.__repr__(), xmlns.__repr__())

    def describe(self):
        text = '''
class Vxml(Scope):
    def __init__(self, version, xml_base, application, xml_lang, xmlns, internal_tags):
        if (version != "2.0" and version != "2.1"):
            raise Exception("bad vxml version")

        if (xmlns is None):
            raise Exception("bad xmlns")

        self.version = version
        self.xmlns = xmlns
        self.xml_base = xml_base
        self.xml_lang = "en-Us" if (xml_lang is None) else xml_lang
        self.application = application

        Scope.__init__(self, internal_tags)

    def run(self):
        for t in self.internal_tags:
            t.run()
'''
        # formCount = False
        # text = ''
        # for t in self.internal_tags:
        # if not ((t is Form) or (t is Menu)) or formCount is False:
        # text += t.describe(1)
        # if t is Form or t is Menu:
        #    formCount = True

        return text


class Form(Scope):
    # may contain field, record, transfer, object, subdialog, initial, block, grammar, var, catch,
    # < block > < catch > < error > < field > < filled > < grammar > < help > < initial > < link > < noinput > < nomatch > < property > < record > < script > < subdialog > < transfer >

    def __init__(self, Id, scope, internal_tags):
        if (scope != None):
            if (scope != "dialog" and scope != "document"):
                raise Exception("bad scope")
            else:
                self.scope = scope
        else:
            self.scope = "dialog"

        self.Id = Id
        if (Id is None):
            # formCng нужен для генерации id формы по нему, реализован как статическая переменная
            try:
                Form.formCnt += 1
            except:
                Form.formCnt = 0
            Id = Form.formCnt

        Scope.__init__(self, internal_tags)

        self.description = 'Form(Id:%s, scope:%s)' % (Id.__repr__(), scope.__repr__())

    def describe(self):
        text = '''
class Form(Scope):
     def __init__(self, Id, scope, internal_tags):
        if (scope != None):
            if (scope != "dialog" and scope != "document"):
                raise Exception("bad scope")
            else:
                self.scope = scope
        else:
            self.scope = "dialog"


        if (Id is None):
            # formCng нужен для генерации id формы по нему, реализован как статическая переменная
            try:
                Form.formCnt += 1
            except:
                Form.formCnt = 0
            self.Id = Form.formCnt
        else: self.Id = Id

        Scope.__init__(self, internal_tags)

        self.last_tag = None
        self.

    def run(self):
        for t in internal_tags:
            if isinstance(t, Script):
                t.evaluate()

        """variables = {}

        for fi in getTags(self.internal_tags, FormItem):
            variables[fi] = None

        for v in getTags(self.internal_tags, Var):
            variables[v[0]] = v[1]

        for s in getTags(self.internal_tags, Script):
            variables[s[0]] = s[1]"""

        while true:

'''

        """
            //
    // Initialization Phase
    //

    foreach ( <var>, <script> and form item, in document order )
       if ( the element is a <var> )
         Declare the variable, initializing it to the value of
         the "expr" attribute, if any, or else to undefined.
       else if ( the element is a <script> )
         Evaluate the contents of the script if inlined or else
         from the location specified by the "src" attribute.
       else if ( the element is a form item )
         Create a variable from the "name" attribute, if any, or
         else generate an internal name.  Assign to this variable
         the value of the "expr" attribute, if any, or else undefined.
                foreach ( input item and <initial> element )
                     Declare a prompt counter and set it to 1.

    if ( user entered this form by speaking to its
          grammar while in a different form)
    {
        Enter the main loop below, but start in
        the process phase, not the select phase:
        we already have a collection to process.
    }

    //
    // Main Loop: select next form item and execute it.
    //

    while ( true )
    {
        //
        // Select Phase: choose a form item to visit.
        //

        if ( the last main loop iteration ended
                  with a <goto nextitem> )
            Select that next form item.

        else if (there is a form item with an
                  unsatisfied guard condition )
            Select the first such form item in document order.n

        else
            Do an <exit/> -- the form is full and specified no transition.

        //
        // Collect Phase: execute the selected form item.
        //
        // Queue up prompts for the form item.

        unless ( the last loop iteration ended with
                a catch that had no <reprompt>,
            and the active dialog was not changed )
        {

            Select the appropriate prompts for an input item or <initial>.
            Queue the selected prompts for play prior to
            the next collect operation.

            Increment an input item's or <initial>'s prompt counter.
        }

        // Activate grammars for the form item.

        if ( the form item is modal )
            Set the active grammar set to the form item grammars,
            if any. (Note that some form items, e.g. <block>,
            cannot have any grammars).
        else
            Set the active grammar set to the form item
            grammars and any grammars scoped to the form,
            the current document, and the application root
            document.

        // Execute the form item.

        if ( a <field> was selected )
            Collect an utterance or an event from the user.
        else if ( a <record> was chosen )
            Collect an utterance (with a name/value pair
            for the recorded bytes) or event from the user.
        else if ( an <object> was chosen )
            Execute the object, setting the <object>'s
            form item variable to the returned ECMAScript value.
        else if ( a <subdialog> was chosen )
            Execute the subdialog, setting the <subdialog>'s
            form item variable to the returned ECMAScript value.
        else if ( a <transfer> was chosen )
            Do the transfer, and (if wait is true) set the
            <transfer> form item variable to the returned
            result status indicator.
        else if ( an <initial> was chosen )
            Collect an utterance or an event from the user.
        else if ( a <block> was chosen )
        {
            Set the block's form item variable to a defined value.

            Execute the block's executable context.
        }

        //
        // Process Phase: process the resulting utterance or event.
        //

        Assign the utterance and other information about the last
        recognition to application.lastresult$.
                // Must have an utterance

        if ( the utterance matched a grammar belonging to a <link> )
          If the link specifies an "next" or "expr" attribute,
          transition to that location.  Else if the link specifies an
          "event" or "eventexpr" attribute, generate that event.

        else if ( the utterance matched a grammar belonging to a <choice> )
          If the choice specifies an "next" or "expr" attribute,
          transition to that location.  Else if the choice specifies
          an "event" or "eventexpr" attribute, generate that event.

        else if ( the utterance matched a grammar from outside the current
                  <form> or <menu> )
        {
          Transition to that <form> or <menu>, carrying the utterance
          to the new FIA.
        }

        // Process an utterance spoken to a grammar from this form.
        // First copy utterance result property values into corresponding
        // form item variables.

        Clear all "just_filled" flags.

        if ( the grammar is scoped to the field-level ) {
           // This grammar must be enclosed in an input item.  The input item
           // has an associated ECMAScript variable (referred to here as the input
           // item variable) and slot name.

           if ( the result is not a structure )
             Copy the result into the input item variable.
           elseif ( a top-level property in the result matches the slot name
                    or the slot name is a dot-separated path matching a
                    subproperty in the result )
             Copy the value of that property into the input item variable.
           else
             Copy the entire result into the input item variable

           Set this input item's "just_filled" flag.
        }
        else {
           foreach ( property in the user's utterance )
           {
              if ( the property matches an input item's slot name )
              {
                 Copy the value of that property into the input item's form
                 item variable.

                 Set the input item's "just_filled" flag.
              }
           }
        }


        // Set all <initial> form item variables if any input items are filled.

        if ( any input item variable is set as a result of the user utterance )
            Set all <initial> form item variables to true.

        // Next execute any triggered <filled> actions.

        foreach ( <filled> action in document order )
        {
            // Determine the input item variables the <filled> applies to.

            N = the <filled>'s "namelist" attribute.

            if ( N equals "" )
            {
               if ( the <filled> is a child of an input item )
                 N = the input item's form item variable name.
               else if ( the <filled> is a child of a form )
                 N = the form item variable names of all the input
                     items in that form.
            }

            // Is the <filled> triggered?

            if ( any input item variable in the set N was "just_filled"
                   AND  (  the <filled> mode is "all"
                               AND all variables in N are filled
                           OR the <filled> mode is "any"
                               AND any variables in N are filled) )
                 Execute the <filled> action.

             If an event is thrown during the execution of a <filled>,
                 event handler selection starts in the scope of the <filled>,
             which could be an input item or the form itself.
        }
        // If no input item is filled, just continue.
    }"""

        '''text = makeTabs(text, level)

        level += 1
        formCount = False

        for t in self.internal_tags:
            if not ((t is Form) or (t is Menu)) or formCount is False:
                text += t.describe(level + 1)
            if t is Form or t is Menu:
                formCount = True'''

        return text


class Goto:
    def __init__(self, expr, expritem, fetchaudio, fetchint, fetchtimeout, maxage, maxstale, next, nextitem):

        i = 0
        if not (expr in None): i += 1
        if not (expritem in None): i += 1
        if not (next in None): i += 1
        if not (nextitem in None): i += 1
        if not (i == 1):
            raise Exception('expr/expritem/next/nextitem only one must be specify')

        self.expr = expr
        self.expritem = expritem
        self.fetchaudio = fetchaudio
        self.fetchint = fetchint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale
        self.next = next
        self.nextitem = nextitem

        self.description = 'Goto(expr:%s, expritem:%s, fetchaudio:%s, fetchint:%s, fetchtimeout:%s, maxage:%s, maxstale:%s, next:%s, nextitem:%s)' % (
        expr, expritem, fetchaudio, fetchint, fetchtimeout, maxage, maxstale, next, nextitem)

    def describe(self):
        return '''
class Goto:
    def __init__(self, expr, expritem, fetchaudio, fetchint, fetchtimeout, maxage, maxstale, next, nextitem):

        i = 0
        if not (expr in None): i += 1
        if not (expritem in None): i += 1
        if not (next in None): i += 1
        if not (nextitem in None): i += 1
        if not (i == 1):
            raise Exception('expr/expritem/next/nextitem only one must be specify')

        self.expr = expr
        self.expritem = expritem
        self.fetchaudio = fetchaudio
        self.fetchint = fetchint
        self.fetchtimeout = fetchtimeout
        self.maxage = maxage
        self.maxstale = maxstale
        self.next = next
        self.nextitem = nextitem

    def run()
        if not (self.expr is None):
            return fetch_ecma_source_uri(self.expr)
        if not (self.expritem is None):
            return fetch_ecma_source(self.expritem)
        if not (self.next is None):
            return fetch_source(self.expritem)
        if not (self.nextitem is None):

            i = 0
            while(len(tags) > i and tags[i].name != self.nextitem and tags[i].id != self.nextitem):
                i += 1

            if (len(tags) > i and (tags[i].name == self.nextitem or tags[i].id == self.nextitem)):
                return tags[i]
'''


class Prompt(Scope):
    # may contain audio, enumerate
    # < audio > <break > < emphasis > < enumerate > < foreach > < mark > < paragraph > < phoneme > < prosody > < say -as > < sentence > < value >

    def __init__(self, bargein, bargeintype, cond, count, timeout, xml_lang, internal_tags, text=''):
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
        self.text = text

        Scope.__init__(self, internal_tags)

        self.description = 'Prompt(bargein:%s, bargeintype:%s, cond:%s, count:%s, timeout:%s, xml_lang:%s)' % (
            bargein.__repr__(), bargeintype.__repr__(), cond.__repr__(), count.__repr__(), timeout.__repr__(),
            xml_lang.__repr__())

    def describe(self):
        return '''
class Prompt(Scope):
    def __init__(self, bargein, bargeintype, cond, count, timeout, xml_lang, internal_tags, text=''):
        self.bargein = True if bargein is None else bargein
        self.bargeintype = True if bargeintype is None else bargeintype
        self.cond = True if cond is None else cond
        self.count = 1 if count is None else count
        self.timeout = 5 if timeout is None else timeout
        self.xml_lang = xml_lang
        self.text = text
        Scope.__init__(self, internal_tags)

    def run(self):
        if ecma_cond(self.cond) is True and self.form.count == self.count:
            playsound(text, bargein, bargeintype, timeout, xml_lang)

'''




class Block(Scope, ControlItem):
    # may contain submit, value, goto
    # < audio > < assign > < clear > < data > < disconnect > < enumerate > < exit > < foreach > < goto > < if > < log > < prompt > < reprompt > <
    # return > < script > < submit > < throw > < value > < var >

    def __init__(self, name, expr, cond, internal_tags):
        """
           name="string"
           expr="ECMAScript_Expression"
           cond="ECMAScript_Expression"
        """
        if (cond == None): cond = True
        ControlItem.__init__(self, name, expr, cond)
        Scope.__init__(self, internal_tags)

        self.description = 'Block(name:%s, expr:%s, cond:%s)' % (name, expr, cond)

    def describe(self):
        text = '''
class Block(Scope, ControlItem):
    def __init__(self, name, expr, cond, internal_tags):

        if (cond == None): cond = True
        ControlItem.__init__(self, name, expr, cond)
        Scope.__init__(self, internal_tags)

    def run(self):
        if ecma_cond(self.cond):
            for t in self.internal_tags:
                t.run()

'''
        # for t in self.internal_tags:
        #   text += t.describe()

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

    def describe(self, level):
        return (makeTabs(['# переделать выражение из ecmascript', '# %s = %s' % (self.name, self.expr)], level))


class Filled:
    # may contain if, clear, assign, return, var
    internalTags = []


class If:
    # may contain assign, exit, else, clear, throw, elseif, submit
    internalTags = []


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
