#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

#import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

import datetime
import time
from calendar import monthrange
import locale

import xlwt
import StringIO

from Mst import *
from Dat import *

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    WorkBook =  self.TableDataSet(self.request.get('LstDate'),int(self.request.get('Kubun')),int(self.request.get('Meigi')))

    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.headers['Content-disposition'] = 'attachment; filename="sakura100.xls"'
    WorkBook.save(self.response.out)

  def TableDataSet(self,Nengetu,Kubun,Meigi):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    WDatMain =  DatMain()
    WDatDenki = DatDenki()
    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  Order by Room"
    SnapDat = db.GqlQuery(Sql)
    MaxRec = SnapDat.count()
    if MaxRec == 0:
      WorkSheet = WorkBook.add_sheet(u'対象データなし' + str(Kubun))  # ダミーシート
      return WorkBook # 終わり

    Styles = self.SetStyles()

    RecDat = SnapDat.fetch(100) # データ取得
    RecCtr = 0
    while (RecCtr < MaxRec): # 全レコード処理したら終わり！

      Rec = ["",""] # レコード退避領域初期化
      Rec[0] = RecDat[RecCtr] # １件目取得
      SheetName = str(Rec[0].Room) # シート名セット
      RecCtr += 1 

      if RecCtr >= MaxRec: # 終わり？
        Rec[1] = ""
      else:
        Rec[1] = RecDat[RecCtr]  # ２件目取得
        SheetName += u"・" + str(Rec[1].Room) # シート名セット
      RecCtr += 1

      WorkSheet = WorkBook.add_sheet(SheetName)  # 新規Excelシート
      self.SetPrintParam(WorkSheet)  # 用紙サイズ等セット

      self.SetColRowSize(WorkSheet) # 行,列サイズセット

      for RowCtr in range(0,2): # １ページ２件
        RowOffset = RowCtr * 18
        self.SetTitle(WorkSheet,RowOffset,Kubun,Meigi,Styles)      # 固定部分セット

        if Kubun == 1:
          Yatin,Kyoeki,Kanri = WDatMain.GetKingaku(Nengetu,Rec[RowCtr],RecYatinMst) # 金額取得
          DenkiDai = 0
        elif Kubun == 2:
          Yatin,Kyoeki,Kanri = WDatMain.GetKingaku(Nengetu,Rec[RowCtr],RecYatinMst) # 金額取得
          DenkiDai = 0
        else:
          Yatin  = 0
          Kyoeki = 0
          Kanri  = 0
          KeisanKubun,Comment,DenkiDai = WDatDenki.GetKingaku(Nengetu,Rec[RowCtr].Room,RecYatinMst.DenkiTanka)

        self.SetKanzyaName(WorkSheet,RowOffset,Rec[RowCtr].KanzyaName,Styles)
        Tuki = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d').month
        self.SetKoumokuName(WorkSheet,RowOffset,Tuki,Kubun,Styles)
        self.SetKingaku(WorkSheet,RowOffset,Kubun,Yatin,Kyoeki,Kanri,DenkiDai,Styles)

        if RecCtr > MaxRec:  
          break

    return  WorkBook

  def SetStyles(self):

    Styles = {}
    
    Style = self.SetStyle(False,"THIN",False,False,False,False)  # Style250
    font = xlwt.Font() # Create the Font
    font.height = 450
    Style.font = font # Apply the Font to the Style
    Styles["Style001"] = Style
 
    Style = self.SetStyle("DOTTED","DOTTED","DOTTED","DOTTED",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER) # Style200
    font = xlwt.Font() # Create the Font
    font.height = 200
    Style.font = font # Apply the Font to the Style
    Styles["Style002"] = Style

    Style = self.SetStyle("DOTTED","DOTTED",False,"DOTTED",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_RIGHT) # Style350
    font = xlwt.Font() # Create the Font
    font.height = 450
    Style.font = font # Apply the Font to the Style
    Styles["Style003"] = Style

    Style = self.SetStyle(False,"THIN",False,False,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 350
    Style.font = font # Apply the Font to the Style
    Styles["Style004"] = Style

    Style = self.SetStyle(False,"THIN",False,False,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    Style = xlwt.XFStyle()
    font.height = 250
    Style.font = font # Apply the Font to the Style
    Styles["Style005"] = Style

    Style = self.SetStyle(False,"THIN",False,False,False,False)
    font = xlwt.Font() # Create the Font
    font.height = 450
    Style.font = font # Apply the Font to the Style
    Styles["Style006"] = Style

    Style = self.SetStyle("DOTTED","DOTTED","DOTTED","DOTTED",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 350
    Style.font = font
    Styles["Style007"] = Style

    Style = self.SetStyle(False,False,False,"DOTTED",False,False) # 008 
    Styles["Style008"] = Style

    Style =  self.SetStyle(False,"DOTTED",False,False,False,False) # 009
    Styles["Style009"] = Style

    Style = self.SetStyle(False,"DOTTED",False,"DOTTED",False,False) 
    Styles["Style010"] = Style

    Style = self.SetStyle(False,"DOTTED",False,"DOTTED",False,False)
    Styles["Style011"] = Style

    Style = self.SetStyle("DOTTED","DOTTED","DOTTED",False,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 350
    Style.font = font
    Styles["Style012"] = Style

    return Styles

  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定
    WorkSheet.set_paper_size_code(13) # B5
    WorkSheet.set_portrait(1) # 縦
    WorkSheet.top_margin = 0.9 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 0.8 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
    WorkSheet.fit_num_pages = 1
    return

  def SetColRowSize(self,WorkSheet):  # 行,列サイズセット

    RowHeight = ["行の高さ",30,30,30,30,30,30,32,30,30,30,60,60,60,30,80,80,20,30]
    for i in range(1,19):
      WorkSheet.row(i - 1).height_mismatch = 1
      WorkSheet.row(i - 1).height = int(RowHeight[i] * 20)
      WorkSheet.row(i + 17).height_mismatch = 1
      WorkSheet.row(i + 17).height = int(RowHeight[i] * 20)

    ColWidth = ["列の幅",10,10,4,3,10,10,4,2,2]
    for i in range(1,10):
      WorkSheet.col(i - 1).width = int(ColWidth[i] * 400)
      WorkSheet.col(i + 8).width = int(ColWidth[i] * 400)

    return

  def SetKanzyaName(self,WorkSheet,RowOffset,KanzyaName,Styles): # 患者名セット

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write_merge(5 + RowOffset,5+ RowOffset,0 + ColSpan ,1 + ColSpan,KanzyaName,Styles["Style001"])
#      WorkSheet.write(5 + RowOffset,0 + ColSpan,KanzyaName,Styles["Style001"]) # Style)
      WorkSheet.write(5 + RowOffset,2 + ColSpan,u"様",Styles["Style001"])

    return

  def SetKoumokuName(self,WorkSheet,RowOffset,Tuki,Kubun,Styles): # 項目名セット

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write( 9 + RowOffset,0 + ColSpan,u""   ,Styles["Style002"])

    if   Kubun == 1:
      Title1 = str(Tuki) + u"月分家賃"
      Title2 = str(Tuki) + u"月分共益費"
    elif Kubun == 2:
      Title1 = str(Tuki) + u"月分管理費"
      Title2 = u" "
    elif Kubun == 3:
      Title1 = str(Tuki) + u"月分電気代"
      Title2 = u" "

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(10 + RowOffset,0 + ColSpan,Title1,Styles["Style002"])
      WorkSheet.write(11 + RowOffset,0 + ColSpan,Title2  ,Styles["Style002"])
      WorkSheet.write(12 + RowOffset,0 + ColSpan," ",Styles["Style002"])

    return
  
  def SetKingaku(self,WorkSheet,RowOffset,Kubun,Yatin,Kyoeki,Kanri,DenkiDai,Styles): # 金額セット

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write( 9 + RowOffset,1 + ColSpan,u"金額"   ,Styles["Style003"])

    if Kubun  == 1:
      Kingaku1 = '{:,d}'.format(Yatin)
      Kingaku2 = '{:,d}'.format(Kyoeki)
    elif Kubun == 2:
      Kingaku1 = '{:,d}'.format(Kanri)
      Kingaku2 = " "
    else:
      Kingaku1 = '{:,d}'.format(int(round(DenkiDai,0)))
      Kingaku2 = " "

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(10 + RowOffset,1 + ColSpan,Kingaku1    ,Styles["Style003"])
      WorkSheet.write(11 + RowOffset,1 + ColSpan,Kingaku2   ,Styles["Style003"])
    
    if   Kubun == 1:
      Goukei = '{:,d}'.format(Yatin + Kyoeki)
    elif Kubun == 2:
      Goukei = '{:,d}'.format(Kanri)
    else:
      Goukei = '{:,d}'.format(int(round(DenkiDai,0)))

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(12 + RowOffset,1 + ColSpan,Goukei ,Styles["Style003"])
      WorkSheet.write(12 + RowOffset,5 + ColSpan,Goukei   ,Styles["Style003"])

    return

  def SetTitle(self,WorkSheet,RowOffset,Kubun,Meigi,Styles):  # 固定部分セット

    Hizuke =  u"平成" + str(datetime.datetime.now().year - 1988) + u"年" 
    Hizuke += str(datetime.datetime.now().month) + u"月"
    Hizuke += str(datetime.datetime.now().day) + u"日"

    WorkSheet.write(1 + RowOffset,0,u"領収書",Styles["Style004"])
    WorkSheet.write(1 + RowOffset,9,u"領収書（控）",Styles["Style004"])

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(0 + RowOffset,5 + ColSpan ,Hizuke,Styles["Style005"])
      if Meigi == 1:
        WorkSheet.write(2 + RowOffset,4 + ColSpan,u"　　呉市宮原２丁目５-２４",Styles["Style005"])
        WorkSheet.write(3 + RowOffset,5 + ColSpan,u"森川　敦子",Styles["Style005"])
        WorkSheet.write(4 + RowOffset,4 + ColSpan,u"　　　　TEL(0823)24-0706",Styles["Style005"])
      else:
        WorkSheet.write(2 + RowOffset,4 + ColSpan,u"　　呉市広白石４丁目７－２２",Styles["Style005"])
        WorkSheet.write(3 + RowOffset,4 + ColSpan,u"　　　医療法人社団　和恒会",Styles["Style005"])
        WorkSheet.write(4 + RowOffset,4 + ColSpan,u"　　　　TEL(0823)70-0555",Styles["Style005"])
        
      if Kubun == 1:
        WorkSheet.write(7 + RowOffset,1 + ColSpan,u"さくらんぼ家賃・共益費" ,Styles["Style006"])
      elif Kubun == 2:
        WorkSheet.write(7 + RowOffset,1 + ColSpan,u"さくらんぼ管理費" ,Styles["Style006"])
      else:
        WorkSheet.write(7 + RowOffset,1 + ColSpan,u"さくらんぼ電気代" ,Styles["Style006"])

      WorkSheet.write(7 + RowOffset,2 + ColSpan,"" ,Styles["Style006"])
      WorkSheet.write(7 + RowOffset,3 + ColSpan,"" ,Styles["Style006"])
      WorkSheet.write(7 + RowOffset,4 + ColSpan,"" ,Styles["Style006"])

      WorkSheet.write_merge(9 + RowOffset,9+ RowOffset,4 + ColSpan ,5 + ColSpan,u"領収印",Styles["Style007"])
      WorkSheet.write_merge(10+ RowOffset,11+ RowOffset,4 + ColSpan ,5 + ColSpan," ",Styles["Style007"])
      WorkSheet.write(12 + RowOffset,4 + ColSpan,u"請求金額"   ,Styles["Style007"])

      WorkSheet.write_merge(14+RowOffset,14+ RowOffset,0 + ColSpan ,0 + ColSpan,u"備考",Styles["Style007"])
      WorkSheet.write_merge(14+RowOffset,14+ RowOffset,1 + ColSpan ,6 + ColSpan," ",Styles["Style007"])

      WorkSheet.write(15 + RowOffset,0 + ColSpan,u"　　この領収書の再発行は致しかねますので、大切に保存してください。")

      WorkSheet.write( 9 + RowOffset,2 + ColSpan,u""     ,Styles["Style012"])
      WorkSheet.write(10 + RowOffset,2 + ColSpan,u"円"   ,Styles["Style012"])
      WorkSheet.write(11 + RowOffset,2 + ColSpan,u"円"   ,Styles["Style012"])
      WorkSheet.write(12 + RowOffset,2 + ColSpan,u"円"   ,Styles["Style012"])
      WorkSheet.write(12 + RowOffset,6 + ColSpan,u"円"   ,Styles["Style012"])

    for i in range(0,16): # ページ切れ目
      WorkSheet.write(i + RowOffset,8,"" ,Styles["Style008"])
#      WorkSheet.write(i + RowOffset,17,"" ,Styles["Style008"])


    if RowOffset == 0:

      WorkSheet.write_merge(16,16,0 ,16," ",Styles["Style009"])

#      for i in range(0,8): # ページ切れ目
#        WorkSheet.write(16 + RowOffset,i,"" ,Styles["Style009"])
#        WorkSheet.write(16 + RowOffset,i + 9,"" ,Styles["Style009"])

#    WorkSheet.write(16 + RowOffset,8,"" ,Styles["Style010"])

#    WorkSheet.write(16 + RowOffset,17,"" ,Styles["Style011"])

    return

  def SetStyle(self,Top,Bottom,Right,Left,Vert,Horz):  # セルスタイルセット

    Style = xlwt.XFStyle()
    Border = xlwt.Borders()
    if Top == "THIN":
      Border.top     = xlwt.Borders.THIN
    elif Top == "DOTTED":
      Border.top     = xlwt.Borders.DOTTED

    if Bottom == "THIN":
      Border.bottom  = xlwt.Borders.THIN
    elif Bottom == "DOTTED":
      Border.bottom     = xlwt.Borders.DOTTED

    if   Left == "THIN":
      Border.left    = xlwt.Borders.THIN
    elif Left == "DOTTED":
      Border.left    = xlwt.Borders.DOTTED

    if   Right == "THIN":
      Border.right   = xlwt.Borders.THIN
    elif Right == "DOTTED":
      Border.right   = xlwt.Borders.DOTTED

    Style.borders = Border

    Alignment      = xlwt.Alignment()

    if Vert != False:
      Alignment.vert = Vert
    if Horz != False:
      Alignment.horz = Horz

    Style.alignment = Alignment

    return Style

app = webapp2.WSGIApplication([
    ('/sakura100/', MainHandler)
], debug=True)
