#!/usr/bin/env python
# -*- coding: UTF-8 -*-
############################
#　電気代一覧印刷(経理部用)
############################

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

    WorkBook =  self.TableDataSet(self.request.get('LstDate'))

    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.headers['Content-disposition'] = 'attachment; filename="sakura116.xls"'
    WorkBook.save(self.response.out)

  def TableDataSet(self,Nengetu):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    WorkSheet = WorkBook.add_sheet(Nengetu.replace("/",u"年") + u"月電気代")  # 新規Excelシート
    self.SetPrintParam(WorkSheet)  # 用紙サイズ等セット
    self.SetColRowSize(WorkSheet) # 行,列サイズセット

    RowOffset = 0
    self.SetTitle(WorkSheet)      # 固定部分セット

    WorkSheet.write(0,1 ,Nengetu.replace("/",u"年") + u"月分電気代")

    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    Sql =  "SELECT * FROM DatMain"  # 家賃データ取得
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  Order by Room"
    SnapDat = db.GqlQuery(Sql)

    RecDat = SnapDat.fetch(100) # データ取得
    OutRow = 2 # 出力行

    Goukei = 0

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
    for Rec in RecDat:
#      if Rec.GenkinFlg == 1: # 現金フラグ立ってる人は # 2015/08/24 現金の人も印刷する！
#        continue  # 出力しない
      OutRow += 1
      OutFlg,Kingaku = self.DataSet(WorkSheet,OutRow,Nengetu,Rec,RecYatinMst.DenkiTanka)
      if OutFlg == False: # 出力対象外
        OutRow -= 1 # やり直し
      else:
        Goukei += Kingaku
        WorkSheet.write(OutRow,0,str(Rec.Room),Style)

    OutRow += 2
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_CENTER)
    WorkSheet.write(OutRow,8,u"当月電気代",Style)
    OutRow += 1
    Style = self.SetStyle(False,False,False,False,False,xlwt.Alignment.HORZ_RIGHT)
    WorkSheet.write(OutRow,7,u"合計額",Style)
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
    WorkSheet.write(OutRow,8,u"￥" + "{:,d}".format(Goukei),Style)

    return  WorkBook

  def DataSet(self,WorkSheet,OutRow,Nengetu,Rec,DenkiTanka):  # データ取得

    WDatDenki = DatDenki()

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)

    KeisanKubun,Comment,Kingaku = WDatDenki.GetKingaku(Nengetu,Rec.Room,DenkiTanka)

    if Kingaku == 0: # ０円の人は印刷しない
      return False,0

    WorkSheet.write(OutRow,2,Rec.KanzyaName,Style) # 患者名
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
    WorkSheet.write(OutRow,1,str(Rec.KanzyaID),Style)

    if Comment == None:
      WorkSheet.write(OutRow,3,"",Style)
    else:
      WorkSheet.write(OutRow,3,Comment,Style)

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)

    Zengetu = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d') # 当月１日
    Zengetu -= datetime.timedelta(days=1) # 前月末日
    ZenMeter = WDatDenki.GetDenki(Zengetu.strftime('%Y/%m'),str(Rec.Room))
    WorkSheet.write(OutRow,4,('%5.2f' % ZenMeter),Style)

    KonMeter = WDatDenki.GetDenki(Nengetu,str(Rec.Room))
    WorkSheet.write(OutRow,5,('%5.2f' % KonMeter),Style)

    WorkSheet.write(OutRow,6,('%5.2f' % (KonMeter - ZenMeter)),Style)

    if KeisanKubun == 1:
      WKingaku = u"手入力"
    else:
      WKingaku = u"￥" + ('%5.2f' % Kingaku)
    WorkSheet.write(OutRow,7,WKingaku,Style)

    WorkSheet.write(OutRow,8,u"￥" + "{:,d}".format(int(round(Kingaku,0))),Style)

    return True,int(round(Kingaku,0))

  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定
#    WorkSheet.set_paper_size_code(13) # B5
    WorkSheet.set_paper_size_code(9) # A4
    WorkSheet.set_portrait(1) # 縦
    WorkSheet.top_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
    WorkSheet.fit_num_pages = 1
    return

  def SetColRowSize(self,WorkSheet):  # 行,列サイズセット

    ColWidth = ["列の幅",0,6,8,0,0,0,8,8,8] # 部屋Noとコメントはいらない

    for i in range(1,10):
      WorkSheet.col(i - 1).width = int(ColWidth[i] * 400) * 2

    return

  def SetTitle(self,WorkSheet):  # 固定部分セット

    Hizuke =  u"平成" + str(datetime.datetime.now().year - 1988) + u"年" 
    Hizuke += str(datetime.datetime.now().month) + u"月"
    Hizuke += str(datetime.datetime.now().day) + u"日"

    WorkSheet.write(0,7 ,Hizuke)

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
    WorkSheet.write(2,0,u"部屋No",Style)
    WorkSheet.write(2,2,u"患者名",Style)
    WorkSheet.write(2,1,u"患者ID",Style)
    WorkSheet.write(2,3,u"コメント",Style)
    WorkSheet.write(2,4,u"前月メータ",Style)
    WorkSheet.write(2,5,u"今月メータ",Style)
    WorkSheet.write(2,6,u"使用料",Style)
    WorkSheet.write(2,7,u"計算額",Style)
    WorkSheet.write(2,8,u"請求額",Style)

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

    font = xlwt.Font() # Create the Font
    font.height = 450
    Style.font = font

    return Style

app = webapp2.WSGIApplication([
    ('/sakura116/', MainHandler)
], debug=True)
