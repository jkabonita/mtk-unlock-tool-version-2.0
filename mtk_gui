#!/usr/bin/env python3
# MTK Flash Client (c) B.Kerler, G.Kreileman 2021.
# Licensed under GPLv3 License
import sys
import time
import mock
import threading
import traceback
import math
import logging
import ctypes
from functools import partial
from PySide6.QtCore import Qt, QVariantAnimation, Signal, QObject, QSize, QTranslator, QLocale, QLibraryInfo, \
    Slot, QCoreApplication
from PySide6.QtGui import QTextOption, QPixmap, QTransform, QIcon, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QLineEdit, \
                            QPushButton

from mtkclient.Library.mtk_class import Mtk
from mtkclient.Library.mtk_da_cmd import DA_handler
from mtkclient.Library.gpt import gpt_settings
from mtkclient.Library.mtk_main import Main, Mtk_Config

from mtkclient.gui.readFlashPartitions import ReadFlashWindow
from mtkclient.gui.writeFlashPartitions import WriteFlashWindow
from mtkclient.gui.eraseFlashPartitions import EraseFlashWindow
from mtkclient.gui.toolsMenu import generateKeysMenu, UnlockMenu
from mtkclient.gui.toolkit import asyncThread, trap_exc_during_debug, convert_size, CheckBox, FDialog, TimeEstim
from mtkclient.config.payloads import pathconfig
from mtkclient.gui.main_gui import Ui_MainWindow
import os

lock = threading.Lock()

os.environ['QT_MAC_WANTS_LAYER'] = '1'  # This fixes a bug in pyside2 on MacOS Big Sur
# TO do Move all GUI modifications to signals!
# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

# Initiate MTK classes
variables = mock.Mock()
variables.cmd = "stage"
variables.debugmode = True
path = pathconfig()
# if sys.platform.startswith('darwin'):
#    config.ptype = "kamakiri" #Temp for Mac testing
MtkTool = Main(variables)

guiState = "welcome"
phoneInfo = {"chipset": "", "bootMode": "", "daInit": False, "cdcInit": False}


class DeviceHandler(QObject):
    sendToLogSignal = Signal(str)
    update_status_text = Signal(str)
    sendToProgressSignal = Signal(int)
    da_handler = None

    def __init__(self, parent, preloader: str = None, loglevel=logging.INFO, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        config = Mtk_Config(loglevel=logging.INFO, gui=self.sendToLogSignal, guiprogress=self.sendToProgressSignal,
                            update_status_text=self.update_status_text)
        config.gpt_settings = gpt_settings(gpt_num_part_entries='0', gpt_part_entry_size='0',
                                           gpt_part_entry_start_lba='0')  # This actually sets the right GPT settings..
        self.loglevel = logging.DEBUG
        self.da_handler = DA_handler(Mtk(config=config, loglevel=logging.INFO), loglevel)



def getDevInfo(self, parameters):
    loglevel = parameters[0]
    phoneInfo = parameters[1]
    devhandler = parameters[2]

    mtkClass = devhandler.da_handler.mtk
    da_handler = devhandler.da_handler
    try:
        if not mtkClass.port.cdc.connect():
            mtkClass.preloader.init()
        else:
            phoneInfo['cdcInit'] = True
    except:
        phoneInfo['cantConnect'] = True
    phoneInfo['chipset'] = str(mtkClass.config.chipconfig.name) + \
                           " (" + str(mtkClass.config.chipconfig.description) + ")"
    self.sendUpdateSignal.emit()
    mtkClass = da_handler.configure_da(mtkClass, preloader=None)
    if mtkClass:
        phoneInfo['daInit'] = True
        phoneInfo['chipset'] = str(mtkClass.config.chipconfig.name) + \
                               " (" + str(mtkClass.config.chipconfig.description) + ")"
        if mtkClass.config.is_brom:
            phoneInfo['bootMode'] = "Bootrom mode"
        elif mtkClass.config.chipconfig.damode:
            phoneInfo['bootMode'] = "DA mode"
        else:
            phoneInfo['bootMode'] = "Preloader mode"
        self.sendUpdateSignal.emit()
    else:
        phoneInfo['cantConnect'] = True
        self.sendUpdateSignal.emit()

def load_translations(application):
    # Load application translations and the QT base translations for the current locale
    locale = QLocale.system()
    translator = QTranslator(application)
    directory = os.path.dirname(__file__)
    lang = 'mtkclient/gui/i18n/' + locale.name()
    if locale.name() == "en_NL":
        lang = lang.replace("en_NL", "nl_NL")
    # lang = 'mtkclient/gui/i18n/fr_FR'
    # lang = 'mtkclient/gui/i18n/de_DE'
    # lang = 'mtkclient/gui/i18n/en_GB'
    # lang = 'mtkclient/gui/i18n/es_ES'
    if translator.load(lang, directory):
        application.installTranslator(translator)

    translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    base_translator = QTranslator(application)
    if base_translator.load(locale, "qtbase", "_", translations_path):
        application.installTranslator(base_translator)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.fdialog = FDialog(self)
        self.initpixmap()
        self.Status = {}
        self.timeEst = TimeEstim()
        self.timeEstTotal = TimeEstim()
        self.ui.logBox.setWordWrapMode(QTextOption.NoWrap)
        self.ui.menubar.setEnabled(False)
        self.ui.tabWidget.setHidden(True)
        self.ui.partProgress.setHidden(True)
        self.ui.fullProgress.setHidden(True)
        self.ui.readDumpGPTCheckbox.setChecked(True)
        self.ui.connectInfo.setMinimumSize(200, 500)
        self.ui.connectInfo.setMaximumSize(9900, 500)
        self.ui.showdebugbtn.clicked.connect(self.showDebugInfo)

        self.devhandler = None
        self.readflash = None

    def showDebugInfo(self):
        self.ui.connectInfo.setHidden(True)
        self.ui.tabWidget.setCurrentWidget(self.ui.debugtab)
        self.ui.tabWidget.setHidden(False)

    @Slot()
    def updateState(self):
        global lock
        lock.acquire()
        doneBytes = 0
        if "currentPartitionSizeDone" in self.Status:
            curpartBytes = self.Status["currentPartitionSizeDone"]
        else:
            curpartBytes = self.Status["currentPartitionSize"]

        if "allPartitions" in self.Status:
            for partition in self.Status["allPartitions"]:
                if self.Status["allPartitions"][partition]['done'] and partition != self.Status["currentPartition"]:
                    doneBytes = doneBytes + self.Status["allPartitions"][partition]['size']
            doneBytes = curpartBytes + doneBytes
            totalBytes = self.Status["totalsize"]
            fullPercentageDone = int((doneBytes / totalBytes) * 100)
            self.ui.fullProgress.setValue(fullPercentageDone)
            timeinfototal = self.timeEstTotal.update(fullPercentageDone, 100)
            self.ui.fullProgressText.setText("<table width='100%'><tr><td><b>Total:</b> " +
                    convert_size(doneBytes) + " / " + convert_size(totalBytes) +
                    "</td><td align='right'>" + timeinfototal + QCoreApplication.translate("main"," left") +
                                             "</td></tr></table>")
        else:
            partBytes = self.Status["currentPartitionSize"]
            doneBytes = self.Status["currentPartitionSizeDone"]
            fullPercentageDone = int((doneBytes / partBytes) * 100)
            self.ui.fullProgress.setValue(fullPercentageDone)
            timeinfototal = self.timeEstTotal.update(fullPercentageDone, 100)
            self.ui.fullProgressText.setText("<table width='100%'><tr><td><b>Total:</b> " +
                convert_size(doneBytes) + " / " + convert_size(partBytes) + "</td><td align='right'>" +
                timeinfototal + QCoreApplication.translate("main"," left") + "</td></tr></table>")

        if "currentPartitionSize" in self.Status:
            partBytes = self.Status["currentPartitionSize"]
            partDone = (curpartBytes / partBytes) * 100
            self.ui.partProgress.setValue(partDone)
            timeinfo = self.timeEst.update(curpartBytes, partBytes)
            txt = "<table width='100%'><tr><td><b>Current partition:</b> " + self.Status["currentPartition"] + \
                  " (" + convert_size(curpartBytes) + " / " + convert_size(partBytes)+") </td><td align='right'>" + \
                timeinfo + QCoreApplication.translate("main"," left")+"</td></tr></table>"
            self.ui.partProgressText.setText(txt)


        lock.release()

    def updateStateAsync(self, toolkit, parameters):
        while not self.Status["done"]:
            # print(self.dumpStatus)
            time.sleep(0.1)
        print("DONE")
        self.ui.readpreloaderbtn.setEnabled(True)
        self.ui.readpartitionsbtn.setEnabled(True)
        self.ui.readboot2btn.setEnabled(True)
        self.ui.readrpmbbtn.setEnabled(True)
        self.ui.readflashbtn.setEnabled(True)

        self.ui.writepartbtn.setEnabled(True)
        self.ui.writeflashbtn.setEnabled(True)
        self.ui.writeboot2btn.setEnabled(True)
        self.ui.writepreloaderbtn.setEnabled(True)
        self.ui.writerpmbbtn.setEnabled(True)

        self.ui.erasepartitionsbtn.setEnabled(True)
        self.ui.eraseboot2btn.setEnabled(True)
        self.ui.erasepreloaderbtn.setEnabled(True)
        self.ui.eraserpmbbtn.setEnabled(True)

    @Slot(int)
    def updateProgress(self, progress):
        try:
            if self.Status["rpmb"]:
                self.Status["currentPartitionSizeDone"] = progress
            else:
                self.Status["currentPartitionSizeDone"] = progress * self.devhandler.da_handler.mtk.daloader.progress.pagesize

            self.updateState()
        except:
            pass

    def setdevhandler(self, devhandler):
        self.devhandler = devhandler
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        devhandler.update_status_text.connect(self.update_status_text)

    def initread(self):
        self.readflash=ReadFlashWindow(self.ui, self, self.devhandler.da_handler, self.sendToLog)
        thread.sendUpdateSignal.connect(win.updateGui)
        self.readflash.enableButtonsSignal.connect(self.enablebuttons)
        self.readflash.disableButtonsSignal.connect(self.disablebuttons)
        self.ui.readpartitionsbtn.clicked.connect(self.readflash.dumpPartition)
        self.ui.readselectallcheckbox.clicked.connect(self.readflash.selectAll)
        self.ui.readpreloaderbtn.clicked.connect(self.on_readpreloader)
        self.ui.readflashbtn.clicked.connect(self.on_readfullflash)
        self.ui.readrpmbbtn.clicked.connect(self.on_readrpmb)
        self.ui.readboot2btn.clicked.connect(self.on_readboot2)

    def initkeys(self):
        self.genkeys = generateKeysMenu(self.ui, self, self.devhandler.da_handler, self.sendToLog)
        self.ui.generatekeybtn.clicked.connect(self.on_generatekeys)
        self.genkeys.enableButtonsSignal.connect(self.enablebuttons)
        self.genkeys.disableButtonsSignal.connect(self.disablebuttons)

    def initunlock(self):
        self.unlock = UnlockMenu(self.ui, self, self.devhandler.da_handler, self.sendToLog)
        self.ui.unlockbutton.clicked.connect(self.on_unlock)
        self.ui.lockbutton.clicked.connect(self.on_lock)
        self.unlock.enableButtonsSignal.connect(self.enablebuttons)
        self.unlock.disableButtonsSignal.connect(self.disablebuttons)

    def initerase(self):
        self.eraseflash = EraseFlashWindow(self.ui, self, self.devhandler.da_handler, self.sendToLog)
        self.eraseflash.enableButtonsSignal.connect(self.enablebuttons)
        self.eraseflash.disableButtonsSignal.connect(self.disablebuttons)
        self.ui.eraseselectallpartitionscheckbox.clicked.connect(self.eraseflash.selectAll)
        self.ui.erasepartitionsbtn.clicked.connect(self.on_erasepartflash)
        self.ui.eraserpmbbtn.clicked.connect(self.on_eraserpmb)
        self.ui.erasepreloaderbtn.clicked.connect(self.on_erasepreloader)
        self.ui.eraseboot2btn.clicked.connect(self.on_eraseboot2)

    def initwrite(self):
        self.writeflash = WriteFlashWindow(self.ui, self, self.devhandler.da_handler, self.sendToLog)
        self.writeflash.enableButtonsSignal.connect(self.enablebuttons)
        self.writeflash.disableButtonsSignal.connect(self.disablebuttons)
        self.ui.writeselectfromdir.clicked.connect(self.writeflash.selectFiles)
        self.ui.writeflashbtn.clicked.connect(self.on_writefullflash)
        self.ui.writepartbtn.clicked.connect(self.on_writepartflash)
        self.ui.writeboot2btn.clicked.connect(self.on_writeboot2)
        self.ui.writepreloaderbtn.clicked.connect(self.on_writepreloader)
        self.ui.writerpmbbtn.clicked.connect(self.on_writerpmb)

    @Slot(str)
    def update_status_text(self, text):
        self.ui.phoneDebugInfoTextbox.setText(text)

    @Slot()
    def disablebuttons(self):
        self.ui.readpreloaderbtn.setEnabled(False)
        self.ui.readpartitionsbtn.setEnabled(False)
        self.ui.readboot2btn.setEnabled(False)
        self.ui.readrpmbbtn.setEnabled(False)
        self.ui.readflashbtn.setEnabled(False)

        self.ui.writeflashbtn.setEnabled(False)
        self.ui.writepartbtn.setEnabled(False)
        self.ui.writepreloaderbtn.setEnabled(False)
        self.ui.writeboot2btn.setEnabled(False)
        self.ui.writerpmbbtn.setEnabled(False)

        self.ui.eraseboot2btn.setEnabled(False)
        self.ui.erasepreloaderbtn.setEnabled(False)
        self.ui.eraserpmbbtn.setEnabled(False)

        self.ui.generatekeybtn.setEnabled(False)
        self.ui.unlockbutton.setEnabled(False)
        self.ui.lockbutton.setEnabled(False)

    @Slot()
    def enablebuttons(self):
        self.ui.readpreloaderbtn.setEnabled(True)
        self.ui.readpartitionsbtn.setEnabled(True)
        self.ui.readboot2btn.setEnabled(True)
        self.ui.readrpmbbtn.setEnabled(True)
        self.ui.readflashbtn.setEnabled(True)

        self.ui.writeflashbtn.setEnabled(True)
        self.ui.writepartbtn.setEnabled(True)
        self.ui.writepreloaderbtn.setEnabled(True)
        self.ui.writeboot2btn.setEnabled(True)
        self.ui.writerpmbbtn.setEnabled(True)

        self.ui.eraseboot2btn.setEnabled(True)
        self.ui.erasepreloaderbtn.setEnabled(True)
        self.ui.eraserpmbbtn.setEnabled(True)

        self.ui.generatekeybtn.setEnabled(True)
        self.ui.unlockbutton.setEnabled(True)
        self.ui.lockbutton.setEnabled(True)
        self.ui.partProgress.setValue(100)
        self.ui.fullProgress.setValue(100)
        self.ui.fullProgressText.setText("")
        self.ui.partProgressText.setText(self.tr("Done."))
        self.Status = {}

    def getpartitions(self):
        data, guid_gpt = self.devhandler.da_handler.mtk.daloader.get_gpt()
        if guid_gpt is None:
            print("Error reading gpt")
            self.ui.readtitle.setText(QCoreApplication.translate("main","Error reading gpt"))
        else:
            self.ui.readtitle.setText(QCoreApplication.translate("main","Select partitions to dump"))

        readpartitionListWidgetVBox = QVBoxLayout()
        readpartitionListWidget = QWidget(self)
        readpartitionListWidget.setLayout(readpartitionListWidgetVBox)
        self.ui.readpartitionList.setWidget(readpartitionListWidget)
        self.ui.readpartitionList.setWidgetResizable(True)
        #self.ui.readpartitionList.setGeometry(10,40,380,320)
        self.ui.readpartitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ui.readpartitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.readpartitionCheckboxes = {}
        for partition in guid_gpt.partentries:
            self.readpartitionCheckboxes[partition.name] = {}
            self.readpartitionCheckboxes[partition.name]['size'] = (partition.sectors * guid_gpt.sectorsize)
            self.readpartitionCheckboxes[partition.name]['box'] = QCheckBox()
            self.readpartitionCheckboxes[partition.name]['box'].setText(partition.name + " (" +
                                                                    convert_size(
                                                                        partition.sectors * guid_gpt.sectorsize) + ")")
            readpartitionListWidgetVBox.addWidget(self.readpartitionCheckboxes[partition.name]['box'])

        writepartitionListWidgetVBox = QVBoxLayout()
        writepartitionListWidget = QWidget(self)
        writepartitionListWidget.setLayout(writepartitionListWidgetVBox)
        self.ui.writepartitionList.setWidget(writepartitionListWidget)
        self.ui.writepartitionList.setWidgetResizable(True)
        #self.ui.writepartitionList.setGeometry(10,40,380,320)
        self.ui.writepartitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ui.writepartitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.writepartitionCheckboxes = {}
        for partition in guid_gpt.partentries:
            self.writepartitionCheckboxes[partition.name] = {}
            self.writepartitionCheckboxes[partition.name]['size'] = (partition.sectors * guid_gpt.sectorsize)
            vb = QVBoxLayout()
            qc=CheckBox()
            qc.setReadOnly(True)
            qc.setText(partition.name + " (" + convert_size(partition.sectors * guid_gpt.sectorsize) + ")")
            hc=QHBoxLayout()
            ll=QLineEdit()
            lb=QPushButton(QCoreApplication.translate("main","Set"))
            lb.clicked.connect(partial(self.selectWriteFile,partition.name,qc,ll))
            hc.addWidget(ll)
            hc.addWidget(lb)
            vb.addWidget(qc)
            vb.addLayout(hc)
            ll.setDisabled(True)
            self.writepartitionCheckboxes[partition.name]['box'] = [qc,ll,lb]
            writepartitionListWidgetVBox.addLayout(vb)

        erasepartitionListWidgetVBox = QVBoxLayout()
        erasepartitionListWidget = QWidget(self)
        erasepartitionListWidget.setLayout(erasepartitionListWidgetVBox)
        self.ui.erasepartitionList.setWidget(erasepartitionListWidget)
        self.ui.erasepartitionList.setWidgetResizable(True)
        #self.ui.erasepartitionList.setGeometry(10,40,380,320)
        self.ui.erasepartitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ui.erasepartitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.erasepartitionCheckboxes = {}
        for partition in guid_gpt.partentries:
            self.erasepartitionCheckboxes[partition.name] = {}
            self.erasepartitionCheckboxes[partition.name]['size'] = (partition.sectors * guid_gpt.sectorsize)
            self.erasepartitionCheckboxes[partition.name]['box'] = QCheckBox()
            self.erasepartitionCheckboxes[partition.name]['box'].setText(partition.name + " (" +
                    convert_size(partition.sectors * guid_gpt.sectorsize)+")")
            erasepartitionListWidgetVBox.addWidget(self.erasepartitionCheckboxes[partition.name]['box'])

    def selectWriteFile(self, partition, checkbox, lineedit):
        fname=self.fdialog.open(partition+".bin")
        if fname is None:
            checkbox.setChecked(False)
            lineedit.setText("")
            lineedit.setDisabled(True)
            return ""
        checkbox.setChecked(True)
        lineedit.setText(fname)
        lineedit.setDisabled(False)
        return fname

    def on_writefullflash(self):
        self.writeflash.writeFlash("user")
        return

    def on_writepreloader(self):
        self.writeflash.writeFlash("boot1")
        return

    def on_writeboot2(self):
        self.writeflash.writeFlash("boot2")
        return

    def on_writerpmb(self):
        self.writeflash.writeFlash("rpmb")
        return

    def on_writepartflash(self):
        self.writeflash.writePartition()
        return

    def on_erasepartflash(self):
        self.eraseflash.erasePartition()
        return

    def on_eraseboot2(self):
        self.eraseflash.eraseBoot2()

    def on_erasepreloader(self):
        self.eraseflash.erasePreloader()

    def on_eraserpmb(self):
        self.eraseflash.eraseRpmb()

    def on_generatekeys(self):
        self.genkeys.generateKeys()

    def on_unlock(self):
        self.unlock.unlock("unlock")

    def on_lock(self):
        self.unlock.unlock("lock")

    def on_readpreloader(self):
        self.readflash.dumpFlash("boot1")

    def on_readboot2(self):
        self.readflash.dumpFlash("boot2")
        return

    def on_readfullflash(self):
        self.readflash.dumpFlash("user")

    def on_readrpmb(self):
        self.readflash.dumpFlash("rpmb")
        return

    def sendToLog(self, info):
        t = time.localtime()
        self.ui.logBox.appendPlainText(time.strftime("[%H:%M:%S", t) + "]: " + info)
        self.ui.logBox.verticalScrollBar().setValue(self.ui.logBox.verticalScrollBar().maximum())

    def sendToProgress(self, progress):
        return

    def updateGui(self):
        global phoneInfo
        phoneInfo['chipset'] = phoneInfo['chipset'].replace("()", "")
        if phoneInfo['cdcInit'] and phoneInfo['bootMode'] == "":
            self.ui.phoneInfoTextbox.setText(QCoreApplication.translate("main","Phone detected:\nReading model info..."))
        else:
            self.ui.phoneInfoTextbox.setText(QCoreApplication.translate("main",
                "Phone detected:\n" + phoneInfo['chipset'] + "\n" + phoneInfo['bootMode']))
        #Disabled due to graphical steps. Maybe this should come back somewhere else.
        #self.ui.status.setText(QCoreApplication.translate("main","Device detected, please wait.\nThis can take a while..."))
        if phoneInfo['daInit']:
            #self.ui.status.setText(QCoreApplication.translate("main","Device connected :)"))
            self.ui.menubar.setEnabled(True)
            self.pixmap = QPixmap(path.get_images_path("phone_connected.png"))
            self.ui.phoneDebugInfoTextbox.setText("")
            self.ui.pic.setPixmap(self.pixmap)
            self.spinnerAnim.stop()
            self.ui.spinner_pic.setHidden(True)
            self.ui.connectInfo.setHidden(True)
            self.ui.partProgress.setHidden(False)
            self.ui.fullProgress.setHidden(False)
            self.ui.tabWidget.setHidden(False)
            self.initread()
            self.initkeys()
            self.initunlock()
            self.initerase()
            self.initwrite()
            self.getpartitions()

        else:
            if 'cantConnect' in phoneInfo:
                self.ui.status.setText(QCoreApplication.translate("main","Error initialising. Did you install the drivers?"))
            self.spinnerAnim.start()
            self.ui.spinner_pic.setHidden(False)

    def spinnerAnimRot(self, angle):
        trans = QTransform()
        dimension = self.pixmap.width() / math.sqrt(2)
        newPixmap = self.pixmap.transformed(QTransform().rotate(angle), Qt.SmoothTransformation)
        xoffset = (newPixmap.width() - self.pixmap.width()) / 2
        yoffset = (newPixmap.height() - self.pixmap.height()) / 2
        rotated = newPixmap.copy(xoffset, yoffset, self.pixmap.width(), self.pixmap.height())
        self.ui.spinner_pic.setPixmap(rotated)

    def initpixmap(self):
        # phone spinner
        self.pixmap = QPixmap(path.get_images_path("phone_loading.png")).scaled(96, 96, Qt.KeepAspectRatio,
                                                                                Qt.SmoothTransformation)
        self.pixmap.setDevicePixelRatio(2)
        self.ui.spinner_pic.setPixmap(self.pixmap)
        self.ui.spinner_pic.show()

        nfpixmap = QPixmap(path.get_images_path("phone_notfound.png"))
        self.ui.pic.setPixmap(nfpixmap)

        logo = QPixmap(path.get_images_path("logo_256.png"))
        self.ui.logoPic.setPixmap(logo)

        initSteps = QPixmap(path.get_images_path("initsteps.png"))
        self.ui.initStepsImage.setPixmap(initSteps)

        self.spinnerAnim = QVariantAnimation()
        self.spinnerAnim.setDuration(3000)
        self.spinnerAnim.setStartValue(0)
        self.spinnerAnim.setEndValue(360)
        self.spinnerAnim.setLoopCount(-1)
        self.spinnerAnim.valueChanged.connect(self.spinnerAnimRot)

        self.ui.spinner_pic.setHidden(True)


if __name__ == '__main__':
    # Enable nice 4K Scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # Init the app window
    app = QApplication(sys.argv)
    load_translations(app)

    win = MainWindow()

    icon = QIcon()
    icon.addFile(path.get_images_path('logo_32.png'), QSize(32, 32))
    icon.addFile(path.get_images_path('logo_64.png'), QSize(64, 64))
    icon.addFile(path.get_images_path('logo_256.png'), QSize(256, 256))
    icon.addFile(path.get_images_path('logo_512.png'), QSize(512, 512))
    app.setWindowIcon(icon)
    win.setWindowIcon(icon)
    if sys.platform.startswith('win'):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MTKTools.Gui')
    dpiMultiplier = win.logicalDpiX()
    if dpiMultiplier == 72:
        dpiMultiplier = 2
    else:
        dpiMultiplier = 1
    addTopMargin = 20
    if sys.platform.startswith('darwin'):  # MacOS has the toolbar in the top bar insted of in the app...
        addTopMargin = 0
    win.setWindowTitle("MTKClient - Version 2.0 beta")
    # lay = QVBoxLayout(self)

    win.show()
    # win.setFixedSize(746, 400 + addTopMargin)

    # Device setup
    loglevel = logging.INFO
    devhandler = DeviceHandler(parent=app, preloader=None, loglevel=loglevel)
    devhandler.sendToLogSignal.connect(win.sendToLog)
    # Get the device info
    thread = asyncThread(parent=app, n=0, function=getDevInfo, parameters=[loglevel, phoneInfo, devhandler])
    thread.sendToLogSignal.connect(win.sendToLog)
    thread.sendUpdateSignal.connect(win.updateGui)
    thread.sendToProgressSignal.connect(win.sendToProgress)
    thread.start()
    win.setdevhandler(devhandler)

    # Run loop the app
    app.exec()
    # Prevent thread from not being closed and call error end codes
    thread.terminate()
    thread.wait()
