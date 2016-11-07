#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  サクランボ請求領収書印刷
#
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
    self.response.headers['Content-disposition'] = 'attachment; filename="sakura101.xls"'
    WorkBook.save(self.response.out)

  def TableDataSet(self,Nengetu,Kubun,Meigi):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    WDatMain =  DatMain()
    WDatDenki = DatDenki()
    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    if Kubun ==1: # 家賃
      Sql =  "SELECT * FROM DatMain"
      Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
      Sql += "  And  Room   < 100" # 2016/05 Add
      Sql += "  Order by Room"
    else:  # 電気代
      Sql =  "SELECT * FROM DatDenki"
      Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
      Sql += "  And  Room   < 100" # 2016/05 Add
      Sql += "  Order by Room"
      
    SnapDat = db.GqlQuery(Sql)
    MaxRec = SnapDat.count()
    if MaxRec == 0:
      WorkSheet = WorkBook.add_sheet(u'対象データなし' + str(Kubun))  # ダミーシート
      return WorkBook # 終わり

    Styles = self.SetStyles()

    for RecDat in SnapDat.fetch(SnapDat.count()): # 全レコード処理

      SheetName = str(RecDat.Room) # シート名セット
      WorkSheet = WorkBook.add_sheet(SheetName)  # 新規Excelシート
      self.SetPrintParam(WorkSheet)  # 用紙サイズ等セット
      self.SetColRowSize(WorkSheet) # 行,列サイズセット
      self.SetTitle(WorkSheet,Nengetu,Kubun,Meigi,Styles)      # 固定部分セット

      if Kubun == 1: # 家賃
        Hozyo,Yatin,Kyoeki,Kanri = WDatMain.GetKingaku(Nengetu,RecDat,RecYatinMst) # 金額取得
        DenkiDai = 0
        Nissu = RecDat.Nissu
      elif Kubun == 2:
        Yatin,Kyoeki,Kanri = WDatMain.GetKingaku(Nengetu,Rec[RowCtr],RecYatinMst) # 金額取得
        DenkiDai = 0
        Nissu = RecDat.Nissu
      else:  # 電気代
        Yatin  = 0
        Kyoeki = 0
        Kanri  = 0
        Nissu = 0
        Siyoryo = WDatDenki.GetSiyoryo(RecDat)
        KeisanKubun,Comment,DenkiDai = WDatDenki.GetKingaku2(Nengetu,RecDat.Room,RecYatinMst.DenkiTanka,Siyoryo)

      self.SetKanzyaName(WorkSheet,RecDat.KanzyaName,Styles)
      self.SetKingaku(WorkSheet,Kubun,Nengetu,Nissu,Yatin,Kyoeki,Kanri,DenkiDai,Styles)

 
    return  WorkBook

  def SetStyles(self):

    Styles = {}
    
    Style = self.SetStyle(False,"THIN",False,False,False,False)  # Style250
    font = xlwt.Font() # Create the Font
    font.height = 450
    Style.font = font # Apply the Font to the Style
    Styles["Style001"] = Style
 
    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER) # Style200
    font = xlwt.Font() # Create the Font
    font.height = 200
    Style.font = font # Apply the Font to the Style
    Styles["Style002"] = Style

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_RIGHT) # Style350
    font = xlwt.Font() # Create the Font
    font.height = 350
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

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_TOP,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 250
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

    RowHeight = [10,10,10,10,10,10,12,10,10,10,10,10,10,10,10,10,10,10] # 行の高さ
    Row = 0
    for Height in RowHeight:
      WorkSheet.row(Row).height_mismatch = 1
      WorkSheet.row(Row).height = int(Height * 60)
      WorkSheet.row(Row + 17).height_mismatch = 1
      WorkSheet.row(Row + 17).height = int(Height * 60)
      Row += 1

    ColWidth = [2,16,2,15,15,2,10,12,2] # 列の幅
    Col = 0
    for Width in ColWidth:
      WorkSheet.col(Col).width = int(Width * 400)
      Col += 1
    return

  def SetKanzyaName(self,WorkSheet,KanzyaName,Styles): # 患者名セット

    for i in range(0,2):
      RowSpan = i * 18
      WorkSheet.write_merge(6 + RowSpan,6 + RowSpan ,0,2,KanzyaName,Styles["Style001"])
#      WorkSheet.write(5,0 + ColSpan,KanzyaName,Styles["Style001"]) # Style)
      WorkSheet.write(6 + RowSpan,3,u"様",Styles["Style005"])

    return

  def SetKoumokuName(self,WorkSheet,Tuki,Kubun,Styles): # 項目名セット

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(9,0 + ColSpan,u""   ,Styles["Style002"])

    if   Kubun == 1:
      Title1 = str(Tuki) + u"月分家賃"
      Title2 = str(Tuki) + u"月分共益費"
      Title3 = str(Tuki) + u"月分管理費"
    elif Kubun == 2:
      Title1 = str(Tuki) + u"月分管理費"
      Title2 = u" "
      Title3 = u" "
    elif Kubun == 3:
      Title1 = str(Tuki) + u"月分電気代"
      Title2 = u" "
      Title3 = u" "

    for i in range(0,2):
      ColSpan = i * 9
      WorkSheet.write(10,0 + ColSpan,Title1,Styles["Style002"])
      WorkSheet.write(11,0 + ColSpan,Title2,Styles["Style002"])
      WorkSheet.write(12,0 + ColSpan,Title3,Styles["Style002"])

    return
  
  def SetKingaku(self,WorkSheet,Kubun,Hizuke,Nissu,Yatin,Kyoeki,Kanri,DenkiDai,Styles): # 金額セット

    if Kubun  == 1:
      Kingaku1 = '{:,d}'.format(Yatin)
      Kingaku2 = '{:,d}'.format(Kyoeki)
      Kingaku3 = '{:,d}'.format(Kanri)
    elif Kubun == 2:
      Kingaku1 = '{:,d}'.format(Kanri)
      Kingaku2 = " "
      Kingaku3 = " "
    else: # 電気代
      Kingaku1 = '{:,d}'.format(int(round(DenkiDai,0)))
      Kingaku2 = " "
      Kingaku3 = " "

    if int(Nissu) == 0: # 日数指定なし
      if int(Hizuke[5:7])== 1: # 1月?
        ZengetuNen = int(Hizuke[0:4]) -1 # 昨年
        Zengetu = 12 # 12月
      else:
        ZengetuNen = int(Hizuke[0:4]) # 当年
        Zengetu = int(Hizuke[5:7]) - 1  # 前月
      if Kubun != 3: # 電気代以外月末締め
        Nissu = monthrange(int(Hizuke[0:4]),int(Hizuke[5:7]))[1] # 末日
      else:  # 電気代は21日締め
        Nissu = monthrange(ZengetuNen,Zengetu)[1] - 21 # 前月日数 - 21
        Nissu += 21 # 当月日数を足す
    OutNissu = str(Nissu) + u"日分"
      
    for i in range(0,2):
      RowSpan = i * 18
      WorkSheet.write_merge(11 + RowSpan,11 + RowSpan,2,3,OutNissu,Styles["Style003"])
      if Kubun != 3:
        WorkSheet.write_merge(12 + RowSpan,12 + RowSpan,2,3,OutNissu,Styles["Style003"])
        WorkSheet.write_merge(13 + RowSpan,13 + RowSpan,2,3,OutNissu,Styles["Style003"])
      else:
        WorkSheet.write_merge(12 + RowSpan,12 + RowSpan,2,3,"",Styles["Style003"])
        WorkSheet.write_merge(13 + RowSpan,13 + RowSpan,2,3,"",Styles["Style003"])
      WorkSheet.write_merge(14 + RowSpan,14 + RowSpan,2,3,"" ,Styles["Style003"])

      WorkSheet.write(11 + RowSpan,4,Kingaku1 ,Styles["Style003"])
      WorkSheet.write(12 + RowSpan,4,Kingaku2 ,Styles["Style003"])
      WorkSheet.write(13 + RowSpan,4,Kingaku3 ,Styles["Style003"])
      WorkSheet.write(14 + RowSpan,4,"" ,Styles["Style003"])
    
    if   Kubun == 1:
#      Goukei = '{:,d}'.format(Yatin + Kyoeki)
      Goukei = '{:,d}'.format(Yatin + Kyoeki + Kanri) + u"円"
    elif Kubun == 2:
      Goukei = '{:,d}'.format(Kanri)
    else:
      Goukei = '{:,d}'.format(int(round(DenkiDai,0))) + u"円"

    for i in range(0,2):
      RowSpan = i * 18
      WorkSheet.write_merge(15 + RowSpan,15 + RowSpan,2,4,Goukei + u"　（税込）",Styles["Style003"])
      WorkSheet.write_merge(13 + RowSpan,15 + RowSpan,7,7,Goukei   ,Styles["Style003"])

    return

  def SetTitle(self,WS,Hizuke,Kubun,Meigi,Styles):  # 固定部分セット

    NowHizuke =  u"平成" + str(datetime.datetime.now().year - 1988) + u"年" 
    NowHizuke += str(datetime.datetime.now().month) + u"月"
    NowHizuke += str(datetime.datetime.now().day) + u"日"
    if int(Hizuke[5:7])== 1: # 1月?
      ZengetuNen = int(Hizuke[0:4]) -1 # 昨年
      Zengetu = 12 # 12月
    else:
      ZengetuNen = int(Hizuke[0:4]) # 当年
      Zengetu = int(Hizuke[5:7]) - 1  # 前月

    if Kubun != 3: # 電気代以外は末日
      TaisyoHizuke =  u"平成"   + str(int(Hizuke[0:4]) - 1988) + u"年" + Hizuke[5:7] + u"月01日～"
      TaisyoHizuke += u"　平成" + str(int(Hizuke[0:4]) - 1988) + u"年" + Hizuke[5:7] + u"月"
      Matubi = monthrange(int(Hizuke[0:4]),int(Hizuke[5:7]))[1] # 前月日数 - 21
      TaisyoHizuke += str(Matubi) + u"日("+ str(Matubi) + u"日間)"
    else:
      TaisyoHizuke =  u"平成"   + str(ZengetuNen - 1988) + u"年" + str(Zengetu) + u"月22日～"
      TaisyoHizuke += u"　平成" + str(int(Hizuke[0:4]) - 1988) + u"年" + Hizuke[5:7] + u"月21日"
      Matubi = monthrange(ZengetuNen,Zengetu)[1] - 21 # 前月日数 - 21
      Matubi += 21 # 当月日数を足す
      TaisyoHizuke += u"(" + str(Matubi) + u"日間)"

    for i in range(0,2):
      RowSpan = i * 18
      WS.write(0 + RowSpan,7 ,NowHizuke,Styles["Style005"])
      WS.write_merge(1 + RowSpan,4 + RowSpan ,7,8,u"領収印",Styles["Style007"])
      WS.write(3 + RowSpan,4,u"医療法人社団和恒会 さくらんぼ",Styles["Style005"])
      WS.write(4 + RowSpan,4,u"呉市広白石４丁目１番１２号",Styles["Style005"])
      WS.write(5 + RowSpan,4,u"  TEL(0823)72-9991",Styles["Style005"])
        
      if Kubun == 1:
        if i == 0:
          WS.write_merge(1,1,1,3,u"さくらんぼ請求領収書" ,Styles["Style006"])
        else:
          WS.write_merge(19,19 ,1,3,u"さくらんぼ請求領収書(控)" ,Styles["Style006"])
        WS.write(8 + RowSpan,1,u"利用内容：外部サービス利用型共同生活援助",Styles["Style005"])
      elif Kubun == 2:
        WS.write(7,1,u"さくらんぼ管理費" ,Styles["Style006"])
        WS.write(8 + RowSpan,1,u"利用内容：外部サービス利用型共同生活援助",Styles["Style005"])
      else:
        if i == 0:
          WS.write_merge(1,1,1,3,u"さくらんぼ請求領収書" ,Styles["Style006"])
        else:
          WS.write_merge(19,19 ,1,3,u"さくらんぼ請求領収書(控)" ,Styles["Style006"])
        WS.write(8 + RowSpan,1,u"利用内容：さくらんぼ個室電気",Styles["Style005"])

      WS.write(9 + RowSpan,1,TaisyoHizuke,Styles["Style005"])
      WS.write(10 + RowSpan,1,u"",Styles["Style002"])
      WS.write_merge(10 + RowSpan,10 + RowSpan,2,3,u"明細" ,Styles["Style002"])
      WS.write(10 + RowSpan,4,u"金額",Styles["Style002"])
      if Kubun != 3:
        WS.write(11 + RowSpan,1,u"室料",Styles["Style002"])
        WS.write(12 + RowSpan,1,u"水道光熱費",Styles["Style002"])
        WS.write(13 + RowSpan,1,u"共用場所維持費",Styles["Style002"])
      else:
        WS.write(11 + RowSpan,1,u"電気代",Styles["Style002"])
        WS.write(12 + RowSpan,1,u"",Styles["Style002"])
        WS.write(13 + RowSpan,1,u"",Styles["Style002"])

      WS.write(14 + RowSpan,1,u"",Styles["Style002"])
      WS.write(15 + RowSpan,1,u"合計",Styles["Style002"])

      WS.write_merge(13 + RowSpan,15 + RowSpan,6,6,u"請求金額" ,Styles["Style002"])
      WS.write(16 + RowSpan,1,u"この領収は再発行しかねますので大切に保管してください。",Styles["Style005"])

#   # ページ切れ目
#    WS.write(17,0,u"―" * 60 ,Styles["Style006"])

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

    Alignment.vert = Vert
    if Horz != False:
      Alignment.horz = Horz

    Style.alignment = Alignment

    return Style

app = webapp2.WSGIApplication([
    ('/sakura101/', MainHandler)
], debug=True)
