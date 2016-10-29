class Vxml:
#may contain form, menu, meta, var, link
	internalTags = []

	def __init__(self, version, xmlns, xml:base, xml:lang, application):
			self.version = version
			self.xmlns = xmlns
			self.xml:base = xml:base
			self.xml:lang = xml:lang
			self.application = application

class Form:
#may contain field, record, transfer, object, subdialog, initial, block, grammar, var, catch, 
	internalTags = []	

	def __init__(self, id):
        	self.id = id

class Subdialog:
#may contain filled
	internalTags = []	

	

class Field:
#may contain grammar, promt,filled, catch, help, option
	internalTags = []	

	def __init__(self, name, expr, cond, ftype, slot, modal):
        	self.name = name
		self.expr = expr
		self.cond = cond
		self.ftype = ftype
		self.slot = slot
		self.modal = modal

class Menu:
#may contain Choice, promt, enumerate, noinput
	internalTags = []	

	def __init__(self, id, dtmf, acccept):
        	self.id = id
		self.dtmf = dtmf
		self.acccept = acccept

class Choice:
#may contain grammar
	internalTags = []	

	def __init__(self, dtmf, acccept, next, expr, event, eventexpr, massage, messageexpr, fetchaudio,fetchhint,fetchtimeout, maxage, maxstale):
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
#may contain repromt, goto, submit, if
	internalTags = []

class Goto:
	pass

class Promt:
#may contain audio, enumerate 
	internalTags = []
	
	def text:
		return 

class Repromt:
	pass

class Initial:
#may contain promt, help, noinput
	internalTags = []

	def __init__(self, name, expr, cond):
        	self.name = name
		self.expr = expr
		self.cond = cond

class Noinput:
#may contain assign
	internalTags = []
	
class Assign:
	pass

class Filled:
#may contain if, clear, assign, return, var
	internalTags = []

class If:
#may contain assign, exit, else, clear, throw, elseif, submit
	internalTags = []

class Block:
#may contain submit, value, goto
	internalTags = []

	def __init__(self, name, expr, cond):
        	self.name = name
		self.expr = expr
		self.cond = cond


class Link:
#may contain grammar
	internalTags = []

class Grammar:
#may contain rule
	internalTags = []

class Rule:
#may contain one-of
	internalTags = []

class Oneof:
#may contain item
	internalTags = []

class Item:
#may contain item
	internalTags = []

class Enumerate:
#may contain value
	internalTags = []

class Option:
	def __init__(self, dtmf, accept, value):
        	self.dtmf = dtmf
		self.accept = accept
		self.value = value
