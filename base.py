# -*- coding: utf8 -*-
import os
import sys
import re
import time
import base64
import uuid
from lxml import etree
import xml.etree.ElementTree as ET
from medialibrary import MediaLibrary, SoundNotFoundError
import utils


class Base:
    messages_dir = os.path.abspath('messages')

    def __init__(self, buddy, params):
        self.buddy = buddy
        self.params = params
        self.last = 0
        self._argv = getattr(params, "sys.argv", None)
        self.mediaLibraryFile = ""
        self.media = None  # initialize media library only when it is needed
        self.default_lang = params.DEFAULT_LANG
        # naumb message
        self._message = None
        # callback tuned flag
        self.callback = False

        # =============== Get OS depended features ============================
        if os.name == 'nt':
            from ntpath import normcase
        else:
            from posixpath import normcase
        self.normcase = normcase
        #======================================================================

    # =============== 1-line functions ========================================
    def playFile(self, fileName):
        """
        Данная функция осуществляет проигрывание указанного аудиофайла.
        Для проигрывания файлов из медиабиблиотеки рекомендуется использовать
        функцию playSound.
        """
        self.buddy.putBuddyCommand('PLAY', self.getAudioPath(fileName))

    def setupCallback(self, count, timeout, st=None, et=None):
        """
        Данная функция настраивает обратный звонок
        """
        params = "%d,%d" % (int(count), int(timeout))
        if bool(st) != bool(et):
            self.buddy.sayDebugMessage('ERROR: can`t set start or end time for callback separately')
            return False
        if st and et:
            params += ",%s,%s" % (st, et)
        self.buddy.putBuddyCommand('CALLBACK', params)
        self.callback = True
        return True

    def blockCall(self):
        """
        Данная функция блокирует вызов, чтобы его не перенаправили до
        окончания проигрывания цельной информации, например Приветствия.
        """
        self.buddy.putBuddyCommand('BLOCK')

    def unblockCall(self):
        """
        Данная функция осуществляет разблокировку заблокированного вызова.
        """
        self.buddy.putBuddyCommand('UNBLOCK')

    def resetAudio(self):
        """
        Данная функция прерывает проигрывание текущего аудиофайла.
        """
        self.buddy.putBuddyCommand('RESET')

    def transferCall(self, number):
        """
        Данная функция осуществляет перенаправление вызова на указанный номер.
        """
        self.buddy.putBuddyCommand('TRANSFER', number)

    def startRecord(self, fileName):
        """
        Данная функция начинает запись указанного аудиофайла (указывается путь
        к записываемому аудиофайлу и его название).
        """
        self.buddy.putBuddyCommand('STARTRECORD', self.normcase(fileName))

    def stopRecord(self):
        """
        Данная функция останавливает запись указанного аудиофайла.
        """
        self.buddy.putBuddyCommand('STOPRECORD')

    def newMailEvent(self, userName):
        """
        Данная функция по указанному логину пользователя посылает ему
        уведомление о приходе новой голосовой почты на голосовой почтовый
        ящик данного пользователя.
        """
        self.buddy.putBuddyCommand('NEWMAIL', userName)
    #==========================================================================

    #============ functions that have some logic ==============================

    def initMediaLib(self, mediaFileName=None):
        """
        Данная функция инициализирует медиабиблиотеку из указанного .imed - файла.
        Она должна быть вызвана перед началом работы с медиабиблиотекой.
        """
        self.mediaLibFile = mediaFileName or getattr(self.params, "MEDIA_LIBRARY", None) or "base.imed"
        self.media = MediaLibrary(self.mediaLibFile)

    #--------------------------------------------------------------------------

    def getVMFolder(self, userName):
        """
        Данная функция по указанному  логину пользователя осуществляет
        переход к папке голосовой почты данного пользователя.
        """
        return self.params.BUDDY_ROOT + '/' + userName + '/vm/'

    #--------------------------------------------------------------------------

    def getVMIntroPath(self, userName):
        """
        Данная функция по указанному логину пользователя выдает путь к файлу
        Приветствия, проигрываемому при входе в Меню Голосовой Почты.
        """
        userIntro = self.getVMFolder(userName) + 'intro.raw'
        if os.path.isfile(self.normcase(userIntro)):
            return userIntro
        else:
            if self.media is None:
                self.initMediaLib()
            return self.media.getSoundFileName('intro_vm', self.params.DEFAULT_LANG)

    #--------------------------------------------------------------------------

    def playVMIntro(self, userName, lang=None):
        """
        Данная функция проигрывает приветствие перед входом в Меню Голосовой Почты
        для указанного пользователя, на указанном языке.
        """
        userIntro = self.getVMFolder(userName) + 'intro.raw'
        if os.path.isfile(self.normcase(userIntro)):
            self.playFile(userIntro)
        else:
            self.playSound("intro_vm", lang)

    #--------------------------------------------------------------------------

    def playSilence(self, count):
        """
        Данная функция проигрывает тишину указанной длительности (длительность
        задается в секундах).
        """
        ten, other = divmod(count, 10)
        five, one = divmod(other, 5)
        for x in xrange(ten):
            self.playSound("silence10")
        for x in xrange(five):
            self.playSound("silence5")
        for x in xrange(one):
            self.playSound("silence1")

    def playSound(self, sound, lang=None):
        """
        Данная функция проигрывает указанный звук из медиабиблиотеки
        на указанном языке.
        """
        lang = lang or self.default_lang
        if self.media is None:
            self.initMediaLib()
        try:
            fileName = self.media.getSoundFileName(sound, lang)
        except SoundNotFoundError as e:
            # emulate older behaviour: send at least something to buddy
            # no file will be played, but buddy will send us ENDIVRQUEUE
            self.buddy.sayDebugMessage('ERROR: %s' % e.message)
            self.buddy.sayDebugMessage('Sending empty PLAY comand to buddy')
            self.buddy.putBuddyCommand('PLAY', '')
        else:
            self.playFile(fileName)

    #--------------------------------------------------------------------------

    def playIntro(self):
        """
        Данная функция проигрывает файл Приветствия.
        """
        self.playSound("intro")
        self.playSilence(self.params.MM_INTRO_PAUSE)

    #--------------------------------------------------------------------------

    def playLongTone(self, tcount):
        """
        Данная функция проигрывает длинный телефонный гудок (КПВ), повторяющийся
        указанное количество раз.
        """
        for x in xrange(tcount):
            self.playSound("longtone")
            self.playSilence(1)

    #--------------------------------------------------------------------------

    def getUserName(self, number):
        """
        Данная функция по указанному телефонному номеру пользователя выдает
        его логин.
        """
        if not number or not len(number):
            return None
        res = self.buddy.askBuddyParam('GETLOGINBYNUMBER', number)
        expr = re.match('FOUNDED:(.+)', res)
        if not expr:
            return None
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def getUserState(self, login):
        """
        Данная функция по указанному логину пользователя выдает текущее
        состояние данного пользователя ("NORMAL", "SPEAKING", "RINGING", "AWAY",
        "DND", "OFFLINE").
        """
        if not login or not len(login):
            return "StateUnknown"
        res = self.buddy.askBuddyParam('GETUSERSTATE', login)
        expr = re.match('STATE:(.+)', res)
        if not expr:
            return "StateUnknown"
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def getUserNumber(self, login):
        """
        Данная функция по указанному логину пользователя выдает его телефонный
        номер.
        """
        if not login or not len(login):
            return None
        res = self.buddy.askBuddyParam("GETNUMBERBYLOGIN", login)
        expr = re.match('FOUNDED:(.+)', res)
        if not expr:
            return None
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def getSessionId(self):
        """
        Данная функция выдает идентификационный номер сессии текущего вызова.
        """
        res = self.buddy.askBuddyParam("GETSESSIONID")
        expr = re.match('SESSIONID:(.+)', res)
        if not expr:
            raise RuntimeError('SESSIONID:result unknow')
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def getCallerId(self, sessionId=''):
        """
        Данная функция по указанному идентификационному номеру сессии выдает
        телефонный номер звонящего пользователя.
        """
        res = self.buddy.askBuddyParam("GETCALLERID", sessionId)
        expr = re.match('CALLERID:(.+)', res)
        if not expr:
            raise RuntimeError('GETCALLERID:result unknow')
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def getCalledId(self):
        """
        Данная функция выдает телефонный номер вызываемого пользователя
        (или номер очереди IVR).
        """
        res = self.buddy.askBuddyParam("GETCALLEDID")
        expr = re.match('CALLEDID:(.+)', res)
        if not expr:
            raise RuntimeError('GETCALLEDID:result unknow')
        return expr.groups()[0]

    #--------------------------------------------------------------------------

    def waitForEndQueue(self):
        """
        Данная функция осуществляет ожидание окончания очереди проигрывания
        файла.
        """
        while not self.buddy.queueEmpty:
            self.buddy.getBuddyEvent()

    #--------------------------------------------------------------------------

    def receiveMessage(self, userName):
        """
        Данная функция по указанному логину пользователя осуществляет запись
        голосового сообщения в папку голосовой почты данного пользователя.
        """
        if not userName:
            sys.exit()
        callerId = self.getCallerId()
        self.playVMIntro(userName)
        self.playSound("beep")
        self.waitForEndQueue()
        self.playSilence(self.params.VM_MAIL_SIZE)
        self.startRecord(self.getVMFolder(userName) + callerId + "_" + str(long(time.time() * 1000)) + ".raw")
        self.newMailEvent(userName)
        self.waitForEndQueue()
        self.playSound("beep")
        self.stopRecord()
        self.newMailEvent(userName)
        self.playSilence(5)
        self.waitForEndQueue()
        sys.exit()

    #--------------------------------------------------------------------------

    def transfer(self, number):
        """
        Данная функция перенаправляет вызов на указанный телефонный номер.
        """
        userName = self.getUserName(number)
        self.resetAudio()
        self.transferCall(number)
        self.playSound("try_transfer")
        while True:
            event = self.buddy.getBuddyEvent()
            if event == 'TRANSFERFAIL':
                break
            if event == 'ENDIVRQUEUE':
                self.playSound("try_transfer")
        self.resetAudio()
        self.receiveMessage(userName)
        return None

    #--------------------------------------------------------------------------

    def waitCallback(self):
        """
        Данная функция предназначена для завершения активного звонка и ожидания обратного вызова абоненту
        Функция должна вызываться после настройки обратного вызова функцией setupCallback
        """
        if not self.callback:
            self.buddy.sayDebugMessage('WARNING: callback not tuned')
            return False
        self.buddy.putBuddyCommand("WAITCALLBACK");
        while True:
            evt = self.buddy.getBuddyEvent()
            if evt == 'CONNECT':
                return True
            if evt == 'HANGUP':
                continue
            if evt.startswith('FAILED'):
                return False
            self.buddy.sayDebugMessage('WARNING: receive unexpected event "%s"' % evt)

    #--------------------------------------------------------------------------

    def getCallerName(self):
        """
        Данная функция предназначена для Меню Голосовой Почты. Проигрывается
        аудиофайл "Введите номер". После того, как пользователь введет свой
        телефонный номер, осуществляется вывод логина данного пользователя.
        """
        while True:
            self.playSound("input_number")
            user_name = self.getUserName(self.getCaller(self.params.USER_MB, self.params.USER))
            self.resetAudio()
            if (user_name is not None):
                return user_name
            self.playSound("subscriber_not_found")
            self.playSilence(1)

    #--------------------------------------------------------------------------

    def getCaller(self, MB, REAL):
        """
        Данная функция по указанным возможному и реальному телефонным номерам
        звонящего пользователя осуществляет вывод телефонного номера данного
        пользователя.
        """
        from operator import truth
        acc = ""
        while True:
            event = self.buddy.getBuddyEvent()
            if(event == self.params.END_OF_INPUT):
                return acc
            if not event.isdigit():
                continue
            acc += event
            if not truth(re.match(MB, acc)):
                return None
            if truth(re.match(REAL, acc)):
                return acc

    #--------------------------------------------------------------------------

    def vm_authorize(self, user, password):
        """
        Данная функция осуществляет авторизацию при входе пользователя в Меню
        Голосовой Почты по введенным пользователем логину и паролю.
        """
        res = self.buddy.askBuddyParam('AUTHORIZE', user + ',' + password)
        if(res == 'AUTHORIZED'):
            return 1
        return None

    #--------------------------------------------------------------------------

    def generateNumberLocalized(self, number, lang='ru', ordinal=False, gender='m', suffix_base=None):
        """
        Данная функция генерирует список аудиофайлов для проговаривания числа
        в заданной форме на заданном языке.
        """
        from nausaynumber import nausaynumber
        if self.media is None:
            self.initMediaLib()
        # Support for older suffix_base param format:
        # convert file path to sound, like
        # /common/audio/en/saynumber/minute/minute -> minute
        # It is done here, not in nausaynumber to be able to inform buddy(and logs) about older format usage.
        if suffix_base and suffix_base.startswith('common/audio'):
            new_suffix_base = suffix_base.split('/')[-1]
            self.buddy.sayDebugMessage('WARNING: generateNumberLocalized called with suffix_base in older format(filepath). '
                                       'Converting to newer format(soundname): "%s" -> "%s"' %
                                       (suffix_base, new_suffix_base))
            suffix_base = new_suffix_base
        sounds = nausaynumber.number_to_sounds(
            int(number), lang, ordinal=ordinal, gender=gender, suffix_base=suffix_base)
        files = []
        many_sound = 'sMany'
        try:
            many_file = self.media.getSoundFileName(many_sound, lang)
        except SoundNotFoundError as e:
            self.buddy.sayDebugMessage(e.message)
            many_file = ''
        for sound in sounds:
            try:
                filename = self.media.getSoundFileName(sound, lang)
                files.append(filename)
            except SoundNotFoundError:
                files.append(many_file)
        self.buddy.sayDebugMessage("Files2Play: " + ' '.join(files))
        return files

    #--------------------------------------------------------------------------

    def sayNumberLocalized(self, number, lang='ru', ordinal=False, gender='m', suffix_base=None):
        """
        Данная функция проигрывает аудиофайлы для заданного числа на заданном языке.
        """
        filelist = self.generateNumberLocalized(number, lang, ordinal, gender, suffix_base)
        for i in filelist:
            self.playFile(i)

    #--------------------------------------------------------------------------

    def recordfile(self, filename, sec):
        """
        Данная функция осуществляет запись аудиофайла, при этом указывается
        его название и длительность.
        """
        self.playSilence(sec)
        self.startRecord(filename)
        while True:
            event = self.buddy.getBuddyEvent()
            if event in ("ENDIVRQUEUE", self.params.END_OF_INPUT):
                break
        self.stopRecord()

    #--------------------------------------------------------------------------

    def playRandomFile(self, files_root):
        """
        Данная функция проигрывает случайный аудиофайл из указанной папки
        с аудиофайлами.
        """
        import random
        files = os.listdir(files_root)
        files = [os.path.normpath(os.path.join(files_root, i)) for i in files]
        files = [os.path.isabs(i) and i or os.path.join(".", i) for i in files]
        files = [i for i in files if os.path.isfile(i)]
        rnd = random.randint(0, len(files) - 1)
        if files:
            self.playFile(files[rnd])

    #--------------------------------------------------------------------------

    def outer_voice_mail(self, user_name=None, lang='ru'):
        """
        Данная функция запрашивает логин и пароль пользователя к его голосой
        почте. При успешном прохождении авторизации пользователь получает доступ
        к своему голосовому почтовому ящику.
        """
        if not user_name:
            user_name = ""
        password = ""
        self.resetAudio()
        while True:
            if not user_name:
                user_name = self.getCallerName()
            self.playSound("input_password")
            password = self.getCaller(self.params.PASSWD_MB, self.params.PASSWD)
            if (self.vm_authorize(user_name, password)):
                break
            self.resetAudio()
            self.playSound("incorrect_password")
        self.listenVoiceMail(user_name, lang=lang)

    #--------------------------------------------------------------------------
    def listenVoiceMail(self, userName, lang='ru'):
        """
        Данная функция по указанному логину пользователя проигрывает голосовые
        сообщения из папки голосовой почты данного пользователя. Далее проигрываются
        аудиофайлы пунктов подменю Меню Голосовой Почты:
        1. Следует нажать "1" для прослушивания предыдущего голосового сообщения;
        2. Следует нажать "2" для удаления данного голосового сообщения;
        3. Сделует нажать "3" для прослушивания следующего голосового сообщения;
        4. Следует нажать "0" для изменения голосового Приветствия, проигрываемого
        при входе в Меню Голосовой Почты.
        При нажатии одной из вышеперечисленных цифр выполняются соответствующие
        действия.
        """
        pointer = 0
        playMessage = None
        playIntro = 1
        while True:
            if playIntro == 1:
                self.playSound("in_your_postbox")
                spfile = []
                userFolder = self.normcase(self.getVMFolder(userName))
                if os.path.isdir(userFolder):
                    spfile = os.listdir(userFolder)
                if "intro.raw" in spfile:
                    spfile.remove("intro.raw")
                self.sayNumberLocalized(
                    len(spfile), lang=lang, gender="n", suffix_base="common/audio/%s/vm/message" % lang)
                if len(spfile):
                    self.playSound("press")
                    self.sayNumberLocalized(1, lang=self.params.DEFAULT_LANG)
                    self.playSound("for_listen_prev_message")
                    self.playSound("press")
                    self.sayNumberLocalized(2, lang=self.params.DEFAULT_LANG)
                    self.playSound("for_delete_this_message")  # this sound does  not exists in russian media lib!
                    self.playSound("press")
                    self.sayNumberLocalized(3, lang=self.params.DEFAULT_LANG)
                    self.playSound("for_listen_next_message")
                self.playSound("press")
                self.sayNumberLocalized(0, lang=self.params.DEFAULT_LANG)
                self.playSound("for_change_intro")
                playIntro = 0
            event = self.buddy.getBuddyEvent()
            if event == self.params.END_OF_INPUT:
                break
            if not event.isdigit():
                continue

            if len(spfile) and event in ('1', '2', '3'):
                if event == '1':
                    pointer -= 1
                    playMessage = 1
                elif event == '2':
                    os.remove(userFolder + spfile[pointer])
                    playIntro = 1
                elif event == '3':
                    pointer += 1
                    playMessage = 1
                if playMessage:
                    pointer += len(spfile)
                    pointer %= len(spfile)
                    self.resetAudio()
                    self.playFile(userFolder + spfile[pointer])
                    self.playSound("beep")
                    self.playSilence(5)
                    playIntro = 1
            if event == '0':
                self.resetAudio()
                self.playSound("change intro")  # sound not exists
                self.playSound("beep")
                self.waitForEndQueue()
                self.recordfile(self.normcase(self.getVMFolder(userName) + 'intro.raw'), 30)
                self.playSound("beep")
                self.playSound("intro_changed")  # sound not exists
                playIntro = 1
            if event == '#':
                break
        self.resetAudio()

    #--------------------------------------------------------------------------

    def isTodayHolyday(self):
        """
        Данная функция определяет, является ли текущий день выходным или
        праздничным днем.
        """
        curtime = time.localtime()
        weekday = curtime.tm_wday

        try:
            with open(self.params.EXCEPTION_DAYS_FILE, "rU") as f:
                exceptions = f.read()
            date = time.strftime('%d/%m/%Y', curtime)
            self.buddy.sayDebugMessage('INFO: date: %s' % date)
            search_expr = "^%s(=[0-6])?$" % date
            sobj = re.search(search_expr, exceptions, re.MULTILINE)
            if sobj:
                if sobj.groups()[0]:
                    weekday = int(sobj.groups()[0][1:])
                else:
                    if weekday < 5:  # пн..пт
                        weekday = 6  # вс
                    else:
                        weekday = 0  # пн
        except IOError as err:
            self.buddy.sayDebugMessage("ERROR: isTodayHolyday error '%s'" % err)

        if weekday > 4:  # сб..вс
            return 1
        return 0

    #--------------------------------------------------------------------------

    def getWorkingWeekDay(self):
        """
        Функция, возвращающая день недели
        """
        curtime = time.localtime()
        weekday = curtime.tm_wday
        return weekday

    #--------------------------------------------------------------------------

    def isTimeBetween(self, mintime, maxtime):
        """
        Данная функция определяет, находится ли текущее время в указанном
        диапазоне времени.
        """
        def convertTime(stime):
            ptime = re.match("^([0-9]{1,2}):([0-9]{2})$", stime)
            if ptime:
                return (int(ptime.groups()[0]), int(ptime.groups()[1]))
            return stime
        if isinstance(mintime, str):
            mintime = convertTime(mintime)
        if isinstance(maxtime, str):
            maxtime = convertTime(maxtime)
        curtime = time.localtime()
        if mintime[0] < 0 or mintime[0] > 23 or mintime[1] < 0 or mintime[1] > 59:
            self.buddy.sayDebugMessage("ERROR: isTimeBetween mintime incorrect '%s'" % str(mintime))
            return 0
        if maxtime[0] < 0 or maxtime[0] > 23 or maxtime[1] < 0 or maxtime[1] > 59:
            self.buddy.sayDebugMessage("ERROR: isTimeBetween maxtime incorrect '%s'" % str(maxtime))
            return 0
        ltime = mintime[0] * 60 + mintime[1]
        htime = maxtime[0] * 60 + maxtime[1]
        ctime = curtime[3] * 60 + curtime[4]
        if ltime > htime:
            if ltime < ctime or ctime < htime:
                return 1
        else:
            if ltime < ctime and ctime < htime:
                return 1
        return 0

    #--------------------------------------------------------------------------

    def getActiveCallsCount(self):
        """
        Данная функция выдает количество активных вызовов в текущий момент
        времени.
        """
        res = self.buddy.askBuddyParam("GETCALLCOUNT")
        expr = re.match('CALLCOUNT:(.+)', res)
        if not expr:
            return int(res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def getQueuedCallsCount(self, queue_id=''):
        """
        Данная функция выдает количество вызовов, находящихся в очереди в
        текущий момент времени.
        """
        res = self.buddy.askBuddyParam("GETQUEUEDCALLSCOUNT", queue_id)
        expr = re.match('QUEUEDCALLSCOUNT:(.+)', res)
        if not expr:
            return int(res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def getPlaceInQueue(self):
        """
        Данная функция возвращает позицию текущего звонка в очереди.
        """
        res = self.buddy.askBuddyParam("GETPLACEINQUEUE")
        expr = re.match('PLACEINQUEUE:(.+)', res)
        if not expr:
            return int(res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def sayAnswerType(self, answerType):
        """
        Если скрипт должен обеспечивать предответ, то команда ANSWER:AlertWithMedia, либо ANSWER:Alert
        должна быть первой командой скрипта, иначе вызов автоматически принимается.
        Если вызов находится в предответе, необходимо дать команду ANSWER:Accept чтобы принять его.
        """
        types = ("Alert", "AlertWithMedia", "Accept")
        if answerType not in types:
                raise ValueError("answerType must be %s, got %s" % (" or ".join(types), answerType))
        self.buddy.putBuddyCommand('ANSWER', answerType)

    def startCallRecord(self):
        """
        Начало записи текущего звонка. Модуль звукозаписи должен быть
        установлен и прописан в лицензии.
        """
        sessionId = self.getSessionId()
        self.setCallParam(sessionId, 'record', 'true')

    def setCallPriority(self, priority=0):
        """
        Команда на установление приоритета вызова в проекте
        (priority - целое число больше 0 или None). Данная команда может быть выполнена
        только в проекте. Приоритет по умолчанию равен 0.
            """
        if priority is None:
            priority = ''
        elif not isinstance(priority, basestring):
            priority = str(priority)
        self.buddy.putBuddyCommand('SETCALLPRIORITY', priority)

    #--------------------------------------------------------------------------

    def setCallPriorityLevel(self, priority=0):
        """
        Команда на установление уровня приоритета звонку.
        """
        if priority is None:
            priority = ''
        elif not isinstance(priority, basestring):
            priority = str(priority)
        self.buddy.putBuddyCommand('SETCALLPRIORITYLEVEL', priority)

    def getCallId(self):
        """
        Функция выполняет запрос и возвращает идентификатор звонка. Используется
        для создания аудиолинков. В случае ошибки возвращает пустую строку.
        """
        res = self.buddy.askBuddyParam("GETCALLID")
        expr = re.match('CALLID:(.+)', res)
        if not expr:
            self.buddy.sayDebugMessage("ERROR: unknown buddy answer '%s'" % res)
            return ''
        return expr.groups()[0]

    def getCallParam(self, sessionId, param):
        """
        Функция выполняет запрос к naubuddyd и возврщает значение запрошенного
        параметра для звонка с идентификатором сессии равным sessionId. В случае
        неудачи возврашает пустую строку. Причины проблем необходимо искать в
        логах naubuddyd.
        """
        params = ','.join((sessionId, param))
        res = self.buddy.askBuddyParam("GETCALLPARAM", params)
        # buddy returns 'callparam:' if not param found
        expr = re.match('CALLPARAM:(.+)', res)
        if not expr:
            self.buddy.sayDebugMessage("ERROR: while getting param '%s'"
                                       % param)
            return ''
        return expr.groups()[0]

    def getGroupMembers(self, groupLogin):
        """
        Возвращает список членов группы с логином groupLogin. В случае ошибки
        список будет пустым. Причину ошибки необходимо смотреть в логах
        naubuddyd.
        """
        res = self.buddy.askBuddyParam("GETGROUPMEMBERS", groupLogin)
        expr = re.match('GROUPMEMBERS:(.+)', res)
        if not expr:
            self.buddy.sayDebugMessage("ERROR: unknown buddy answer '%s'"
                                       % res)
            return []
        members = expr.groups()[0].split(',')
        return members

    def changeCallProject(self, projectId):
        """
        Команда на смену проекта звонка. В случае отсутствия проекта с указанным
        Id проблему надо искать в логах naubuddyd.
        """
        self.buddy.putBuddyCommand('CHANGECALLPROJECT', projectId)

    def sendFax(self, fileName, setCodec=False):
        """
        Команда на отправку tiff файла удалённой стороне. Путь до файла может
        быть как относительным, так и абсолютным. Возвращает либо 'FAILED', либо
        'SUCCESS'. При неудаче причину выводит в лог скрипта.
        """
        params = ','.join((fileName, 'setCodec' if setCodec else 'noCodec'))
        res = self.buddy.askBuddyParam('SENDFAX', params)
        if res.startswith('FAILED'):
            self.buddy.sayDebugMessage('ERROR: %s' % res)
            return 'FAILED'
        if res.startswith('SUCCESS'):
            return int(res.split(':')[1])
        return res

    def receiveFax(self, fileName):
        """
        Команда на приём tiff файла от удалённой стороны. Путь до файла может
        быть как относительным, так и абсолютным. Возвращает либо 'FAILED', либо
        'SUCCESS'. При неудаче причину выводит в лог скрипта.
        """
        res = self.buddy.askBuddyParam('RECEIVEFAX', fileName)
        if res.startswith('FAILED'):
            self.buddy.sayDebugMessage('ERROR: %s' % res)
            return 'FAILED'
        if res.startswith('SUCCESS'):
            return int(res.split(':')[1])
        return res

    def pickupCall(self):
        """
        Команда на перехват вызова, направленного другому члену той же первичной
        группы, что и звонящий(caller) на IVR.
        """
        res = self.buddy.askBuddyParam('CALLPICKUP')
        if res.startswith('FAILED'):
            self.buddy.sayDebugMessage('ERROR: %s' % res)
            return 'FAILED'
        return 'SUCCESS'

    def parkCall(self, parkId):
        """
        Запрос на парковку вызова с идентификатором parkId. Идентификатором
        может служить любая строка.
        """
        res = self.buddy.askBuddyParam('CALLPARK', parkId)
        if res.startswith('FAILED'):
            self.buddy.sayDebugMessage('ERROR: %s' % res)
            return 'FAILED'
        return 'SUCCESS'

    def unparkCall(self, parkId):
        """
        Запрос на приём звонка с идентификатором parkId, стоящего на парковке.
        """
        res = self.buddy.askBuddyParam('CALLUNPARK', parkId)
        if res.startswith('FAILED'):
            self.buddy.sayDebugMessage('ERROR: %s' % res)
            return 'FAILED'
        return 'SUCCESS'

    def stopTransfer(self):
        """
        Команда на прерывание перевода звонка. В случае, если звонок не
        находится в состоянии перевода - в логе naubuddyd будет сообщение
        об ошибке.
        """
        self.buddy.putBuddyCommand('STOP_CONSULTATION')

    def setTimeOut(self, timeout):
        """
        Команда на установку таймера, в мс. По истечение времени скриптом будет
        получено событие TIMEDOUT. Таймер можно устанавливать только один. Если
        с данным скриптом связан другой таймер, то вызов данной функции прервёт
        его выполнение и будет установлен новый таймер.
        """
        if not isinstance(timeout, basestring):
            timeout = str(timeout)
        self.buddy.putBuddyCommand('TIMEOUT', timeout)

    def setCallParam(self, sessionId, param, value):
        """
        Команда на установку звонку параметра param в значение value.
        Идентификатор сессии (sessionId) должен быть предварительно получен
        вызовом self.getSessionId().
        """
        if '\n' in value:
            params = ','.join((sessionId, param,  base64.b64encode(value)))
            self.buddy.putBuddyCommand('SETCALLPARAMBASE64', params)
        else:
            params = ','.join((sessionId, param, value))
            self.buddy.putBuddyCommand('SETCALLPARAM', params)
    #--------------------------------------------------------------------------

    def createAudioLink(self, callIdFrom, callIdTo, type_='input2output'):
        """
        Запрос на создание аудио-линка. Тип может быть один из 'input2input',
        'input2output', 'output2input', 'output2output'.
        """
        res = 'FAILURE'
        if type_ not in ('input2input', 'input2output',
                         'output2input', 'output2output'):
            self.buddy.sayDebugMessage("ERROR: unknown link type '%s'" % type_)
        else:
            param = ','.join((callIdFrom, callIdTo, type_))
            answer = self.buddy.askBuddyParam("CREATEAUDIOLINK", param)
            expr = re.match('CREATEAUDIOLINK:(.+)', answer)
            if not expr:
                self.buddy.sayDebugMessage("ERROR: unknown buddy answer '%s'"
                                           % answer)
            else:
                res = expr.groups()[0]
        return res

    def destroyAudioLink(self, callIdFrom, callIdTo, type_='input2output'):
        """
        Запрос на разрушения аудио-линка.
        """
        res = 'FAILURE'
        if type_ not in ('input2input', 'input2output',
                         'output2input', 'output2output'):
            self.buddy.sayDebugMessage("ERROR: unknown link type '%s'" % type_)
        else:
            param = ','.join((callIdFrom, callIdTo, type_))
            answer = self.buddy.askBuddyParam("DESTROYAUDIOLINK", param)
            expr = re.match('DESTROYAUDIOLINK:(.+)', answer)
            if not expr:
                self.buddy.sayDebugMessage("ERROR: unknown buddy answer '%s'"
                                           % answer)
            else:
                res = expr.groups()[0]
        return res
    #--------------------------------------------------------------------------

    def getWorkingOperatorsCount(self, queue_id=''):
        """
        Данная функция возвращает количество операторов, находящихся в данный
        момент времени в состоянии "NORMAL", "SPEAKING" или "RINGING".
        """
        res = self.buddy.askBuddyParam("GETWORKINGOPERATORSCOUNT", queue_id)
        expr = re.match('WORKINGOPERATORSCOUNT:(.+)', res)
        if not expr:
            return int(res)
        return int(expr.groups()[0])

    def getOnlineOperatorsCount(self, queue_id=''):
        """
        Данная функция возвращает количество операторов, находящихся в данный
        момент времени не в состоянии "offline".
        """
        res = self.buddy.askBuddyParam("GETONLINEOPERATORSCOUNT", queue_id)
        expr = re.match('ONLINEOPERATORSCOUNT:(.+)', res)
        if not expr:
            return int(res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def getReadyOperatorsCount(self, queue_id=''):
        """
        Данная функция выдает количество операторов, готовых принять звонок
        в данный момент времени.
        """
        res = self.buddy.askBuddyParam("GETREADYOPERATORSCOUNT", queue_id)
        expr = re.match('READYOPERATORSCOUNT:(.+)', res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def getTotalQueuedCallsCount(self, queue_id=''):
        """
        Функция возвращает количество вызовов ожидающих ответа по указанному проекту.
        """
        res = self.buddy.askBuddyParam("GETTOTALQUEUEDCALLSCOUNT", queue_id)
        expr = re.match('TOTALQUEUEDCALLSCOUNT:(.+)', res)
        return int(expr.groups()[0])

    #--------------------------------------------------------------------------

    def getMaxWaitTime(self, queue_id=''):
        """
        Функция возвращает время в секундах, показывающее сколько ожидает
         самый старый звонок в проекте.
        """
        res = self.buddy.askBuddyParam("GETMAXWAITTIME", queue_id)
        expr = re.match('MAXWAITTIME:(.+)', res)
        return int(expr.groups()[0])

    def playTree(self, folder):
        folder_stack = [folder]

        new_folder = 1
        while True:
            if new_folder:
                current_folder = "/".join(folder_stack)
                if os.path.isfile("%s/intro.raw" % (current_folder,)):
                    self.playFile("%s/intro.raw" % (current_folder))
                new_folder = 0
            ev = self.buddy.getBuddyEvent()
            if ev == "#":
                del folder_stack[len(folder_stack) - 1:]
                if not folder_stack:
                    return
            if ev in "0123456789":
                if os.path.isdir("%s/%s" % ("/".join(folder_stack), ev)):
                    folder_stack.append(ev)
                    new_folder = 1

    #--------------------------------------------------------------------------

    def getAudioPath(self, path):
        if path.startswith(".") or path.startswith("/"):
            return self.normcase(path)
        else:
            return self.normcase(self.params.AUDIO_ROOT + "/" + path)

    #--------------------------------------------------------------------------

    def getNumberCategories(self, number):
        """
        Данная функция выдает для указанного номера список категорий.
        """
        res = self.buddy.askBuddyParam("GETNUMBERCATEGORIES", number)
        expr = re.match('SUCCESS:(.+)', res)
        if not expr:
            self.buddy.sayDebugMessage("error in 'GETNUMBERCATEGORIES': %s" % res)
            return None
        else:
            categories = expr.groups()[0].split(',')
            return categories

    #===============================ASR/TTS====================================
    def sayText(self, text):
        """
        Сказать фразу, используя Text-To-Speech
        @text: xml с корневым тегом Speak
        """
        res = self.buddy.askBuddyParam("SPEAK", base64.b64encode(text))
        if res.startswith('FAILED'):
            return 'FAILED'
        return 'SUCCESS'

    #--------------------------------------------------------------------------

    def startRecognition(self, recogn):
        """
        Начать распознавание
        @recogn: xml с корневым тегом Recognition
        """
        res = self.buddy.askBuddyParam("START_RECOGNITION", base64.b64encode(recogn))
        if res.startswith('FAILED'):
            return 'FAILED'
        return 'SUCCESS'

    #--------------------------------------------------------------------------

    def stopRecognition(self):
        """
        Остановить распознавание, начатое командой startRecognition
        """
        self.buddy.putBuddyCommand("STOP_RECOGNITION")

    def setHangupReason(self, text, code=None):
        """
        Данная функция осуществляет установку причины завершения звонка(при завершении скрипта)
        """
        param = text
        if code:
            param += ',' + str(code)
        self.buddy.putBuddyCommand('SETHANGUPREASON', param)

    def setSecureMode(self, secure):
        """
        Данная функция осуществляет установку режима безопасности PCI DSS
        """
        param = 'true' if secure else 'false'
        self.buddy.putBuddyCommand('SET_SECURE_MODE', param)


    #--------------------------------------------------------------------------
    # MessageBox commands
    #--------------------------------------------------------------------------
    def getMessage(self):
        """
        Данная функция запрашивает у NauMB сообщение
        """
        if self._message is not None:
            return self._message
        res = self.buddy.askBuddyParam('GETMESSAGE')
        message_filepath = re.match('MESSAGE:(.+)', res).groups()[0]
        xml_tree = ET.parse(message_filepath)
        message = xml_tree.getroot()
        self._message = message
        return message

    def _is_email(self):
        if self._message is None:
            self.getMessage()
        params_element = self._message.find('Params')
        return params_element.get('content_type') == 'message/rfc822'

    def getMessageField(self, field_name):
        """
        Данная функция возвращает значение поля сообщения. Одного из:
         * content_type
         * content
         * created
         * from_addr
         * to_addr
         * message_id
         * reply_id
         * session_id
         * subject
         * text

        для email сообщений также возможно получить произвольный MIME заголовок
        """
        if self._message is None:
            self.getMessage()

        def get_content():
            content_element = self._message.find('Content')
            return content_element.text
        field_name = field_name.lower()
        params_element = self._message.find('Params')

        is_email = self._is_email()

        if field_name == 'content':
            # raw content
            return get_content()
        if field_name == 'text':
            content = get_content()
            if is_email:
                return utils.get_email_message_text(content)
            else:
                return content

        field = params_element.get(field_name)
        if field is not None:
            return field
        elif is_email:
            content = get_content()
            try:
                return utils.get_email_message_header(content, field_name)
            except Exception as exc:
                self.buddy.sayDebugMessage("exception occurred in 'getMessageField': %s" % exc)
                return ''
        else:
            return ''

    def sendMessage(self, content, from_addr='', to_addr='', subject='', email_text_only=False):
        """
        Данная функция позволяет отправить дискретное сообщение.
        @content: содержимое
        @from_addr: адрес отправителя, необязательный
        @to_addr: адрес получателя, необязательный
        @subject: тема письма, необязятельный
        @email_text_only: True - @content содержит только текст и будет закодирован
                          False - @content будет отправлен без изменений
        """
        content = utils.to_unicode(content)
        element = etree.Element('Message')
        params_element = etree.SubElement(element, 'Params')
        params_element.set('from_addr', utils.to_unicode(from_addr))
        params_element.set('to_addr', utils.to_unicode(to_addr))
        params_element.set('subject', utils.to_unicode(subject))
        content_element = etree.SubElement(element, 'Content')
        if self._is_email() and email_text_only:
            content = utils.encode_mime_text(content)
        content_element.text = etree.CDATA(content)
        tree = element.getroottree()
        if not os.path.exists(self.messages_dir):
            os.makedirs(self.messages_dir)
        filename = os.path.join(self.messages_dir, '%s_%s.xml' % (self.getSessionId(), uuid.uuid1().hex))
        with open(filename, 'w') as msg_file:
            tree.write(msg_file, encoding='utf-8', xml_declaration=True)
        self.buddy.putBuddyCommand('SENDMESSAGE', filename)

    def getFlexValue(self, flex_id):
        """
        Данная функция возвращает значение Флекс-атрибута кейса по его flex_id.
        Имеет смысл для вызовов созданных Dialer'ом
        """
        if not hasattr(self, 'flex_attributes'):
            import argparse
            import urllib
            import json
            arg_parser = argparse.ArgumentParser()
            arg_parser.add_argument('--flex_attributes')
            args, _ = arg_parser.parse_known_args(self._argv[2:])
            if not args.flex_attributes:
                self.flex_attributes = {}
            else:
                self.flex_attributes = json.loads(urllib.unquote(args.flex_attributes))
        return self.flex_attributes.get(flex_id, '')

    def reportMessagePlayed(self):
        """
        Данная функция уведомляет Dialer об успешном проигрывании
        сообщения абоненту
        """
        self.buddy.putBuddyCommand('REPORTMESSAGEPLAYED')

    def getMessageNumber(self):
        """
        Данная функция возвращает порядковый номер дискретного
        сообщения в сессии
        """
        res = self.buddy.askBuddyParam('GETMESSAGENUMBER')
        msg_num = int(re.match('MESSAGENUMBER:(.+)', res).groups()[0])
        return msg_num
