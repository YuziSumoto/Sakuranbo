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

    WorkBook =  self.TableDataSet(self.request.get('LstDate'),int(self.request.get('Kubun')))

    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.headers['Content-disposition'] = 'attachment; filename="sakura110.xls"'
    WorkBook.save(self.response.out)

  def TableDataSet(self,Nengetu,Kubun):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    WorkSheet = WorkBook.add_sheet(Nengetu.replace("/",u"年") + u"月家賃共益費")  # 新規Excelシート
    self.SetPrintParam(WorkSheet)  # 用紙サイズ等セット
    self.SetColRowSize(WorkSheet) # 行,列サイズセット

    RowOffset = 0
    self.SetTitle(WorkSheet,Kubun)      # 固定部分セット

    WorkSheet.write(0,1 ,Nengetu.replace("/",u"年") + u"月分家賃・共益費")

#    Sql =  "SELECT * FROM MstRoom"
#    Sql += "  Order by Room"

#    SnapDat = db.GqlQuery(Sql)

#    RecDat = SnapDat.fetch(100) # データ取得
    OutRow = 2 # 出力行

    DaityoKei = [0,0,0]
    GenkinKei = [0,0,0]

    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font

#    for Rec in RecDat:
    OutRow += 1
    OutRow = self.DataSet(WorkSheet,OutRow,Nengetu,DaityoKei,GenkinKei,RecYatinMst)

    OutRow += 1
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 200
    Style.font = font
    WorkSheet.write(OutRow,4,u"家賃+水道光熱費",Style)
    WorkSheet.write(OutRow,9,u"家賃",Style)
    WorkSheet.write(OutRow,10,u"水道光熱費",Style)
    WorkSheet.write(OutRow,11,u"共用場所維持費",Style)
    OutRow += 1
    Style = self.SetStyle(False,False,False,False,False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(OutRow,3,u"台帳引き",Style)
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(OutRow,4,u"￥" + "{:,d}".format(DaityoKei[0] + DaityoKei[1]),Style)
    WorkSheet.write(OutRow,9,u"￥" + "{:,d}".format(DaityoKei[0]),Style)
    WorkSheet.write(OutRow,10,u"￥" + "{:,d}".format(DaityoKei[1]),Style)
    WorkSheet.write(OutRow,11,u"￥" + "{:,d}".format(DaityoKei[2]),Style)
    OutRow += 1
    Style = self.SetStyle(False,False,False,False,False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(OutRow,3,u"現金",Style)
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(OutRow,4,u"￥" + "{:,d}".format(GenkinKei[0] + GenkinKei[1]),Style)
    WorkSheet.write(OutRow,9,u"￥" + "{:,d}".format(GenkinKei[0]),Style)
    WorkSheet.write(OutRow,10,u"￥" + "{:,d}".format(GenkinKei[1]),Style)
    WorkSheet.write(OutRow,11,u"￥" + "{:,d}".format(GenkinKei[2]),Style)
    OutRow += 1
    Style = self.SetStyle(False,False,False,False,False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(OutRow,3,u"合計額",Style)
    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    Goukei  = DaityoKei[0] + DaityoKei[1]
    Goukei += GenkinKei[0] + GenkinKei[1]
    WorkSheet.write(OutRow,4,u"￥" + "{:,d}".format(Goukei),Style)
    Goukei  = DaityoKei[0] + GenkinKei[0]
    WorkSheet.write(OutRow,9,u"￥" + "{:,d}".format(Goukei),Style)
    Goukei  = DaityoKei[1] + GenkinKei[1]
    WorkSheet.write(OutRow,10,u"￥" + "{:,d}".format(Goukei),Style)
    Goukei  = DaityoKei[2] + GenkinKei[2]
    WorkSheet.write(OutRow,11,u"￥" + "{:,d}".format(Goukei),Style)


    return  WorkBook

  def DataSet(self,WorkSheet,OutRow,Nengetu,DaityoKei,GenkinKei,RecYatinMst):  # データ取得

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   < 100" # + Room
    Sql += "  Order by Room"

    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      return OutRow

    for RecDat in Snap.fetch(Snap.count()):

      Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
      font = xlwt.Font() # Create the Font
      font.height = 250
      Style.font = font
      WorkSheet.write(OutRow,0,str(RecDat.Room),Style) # 患者名 

      WorkSheet.write(OutRow,2,RecDat.KanzyaName,Style) # 患者名 

      Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
      font = xlwt.Font() # Create the Font
      font.height = 250
      Style.font = font
      WorkSheet.write(OutRow,1,str(RecDat.KanzyaID),Style)

      Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
      font = xlwt.Font() # Create the Font
      font.height = 250
      Style.font = font
      WorkSheet.write(OutRow,3,RecDat.IONaiyo,Style)

      WorkSheet.write(OutRow,4,RecDat.Zyokyo,Style)

      Style = self.SetStyle("THIN","THIN","THIN","THIN",False,xlwt.Alignment.HORZ_RIGHT)
      font = xlwt.Font() # Create the Font
      font.height = 250
      Style.font = font

      if  RecDat.Nissu == None or RecDat.Nissu == 0:
        WorkSheet.write(OutRow,5,"",Style)
      else:
        WorkSheet.write(OutRow,5,str(RecDat.Nissu),Style)

      if  RecDat.NyuinNissu == None or RecDat.NyuinNissu == 0:
        WorkSheet.write(OutRow,6,"",Style)
      else:
        WorkSheet.write(OutRow,6,str(RecDat.NyuinNissu),Style)
      if  RecDat.TaikenNissu == None or RecDat.TaikenNissu == 0:
        WorkSheet.write(OutRow,7,"",Style)
      else:
        WorkSheet.write(OutRow,7,str(RecDat.TaikenNissu),Style)

      Hozyo,Yatin,Kyoeki,Kanri =  DatMain().GetKingaku(Nengetu,RecDat,RecYatinMst)
      WorkSheet.write(OutRow,8,u"￥" + "{:,d}".format(Hozyo),Style)
      WorkSheet.write(OutRow,9,u"￥" + "{:,d}".format(Yatin),Style)
      WorkSheet.write(OutRow,10,u"￥" + "{:,d}".format(Kyoeki),Style)
      WorkSheet.write(OutRow,11,u"￥" + "{:,d}".format(Kanri),Style)

      Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
      font = xlwt.Font() # Create the Font
      font.height = 250
      Style.font = font
      if RecDat.GenkinFlg == 1:
        GenkinKei[0] += Yatin
        GenkinKei[1] += Kyoeki
        GenkinKei[2] += Kanri
        font = xlwt.Font() # Create the Font
        font.height = 450
        Style.font = font
        WorkSheet.write(OutRow,12,u"○",Style)
      else:
        DaityoKei[0] += Yatin
        DaityoKei[1] += Kyoeki
        DaityoKei[2] += Kanri
        WorkSheet.write(OutRow,12,"",Style)
      OutRow += 1

    return OutRow

  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定
#    WorkSheet.set_paper_size_code(13) # B5
    WorkSheet.set_paper_size_code(9) # A4
    WorkSheet.set_portrait(1) # 縦
    WorkSheet.top_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 1.5 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
    WorkSheet.fit_num_pages = 1
    return

  def SetColRowSize(self,WorkSheet):  # 行,列サイズセット

    ColWidth = ["列の幅",4,6,8,10.5,10.5,4,4,4,7,10,10,14,8]
    for i in range(1,14):
      WorkSheet.col(i - 1).width = int(ColWidth[i] * 400)

    for i in range(1,50):
      WorkSheet.row(i - 1).height_mismatch = 1
      WorkSheet.row(i - 1).height = int(20 * 20)

    return

  def SetTitle(self,WorkSheet,Kubun):  # 固定部分セット

    Hizuke =  u"平成" + str(datetime.datetime.now().year - 1988) + u"年" 
    Hizuke += str(datetime.datetime.now().month) + u"月"
    Hizuke += str(datetime.datetime.now().day) + u"日"

    WorkSheet.write(0,7 ,Hizuke)

    Style = self.SetStyle("THIN","THIN","THIN","THIN",False,False)
    font = xlwt.Font() # Create the Font
    font.height = 250
    Style.font = font
    WorkSheet.write(2,0,u"部屋",Style)
    WorkSheet.write(2,1,u"患者名",Style)
    WorkSheet.write(2,2,u"患者ID",Style)
    WorkSheet.write(2,3,u"移動区分",Style)
    WorkSheet.write(2,4,u"状況",Style)
    WorkSheet.write(2,5,u"利日",Style)
    WorkSheet.write(2,6,u"入日",Style)
    WorkSheet.write(2,7,u"体日",Style)
    WorkSheet.write(2,8,u"補助",Style)
    WorkSheet.write(2,9,u"家賃",Style)
    WorkSheet.write(2,10,u"水道光熱費",Style)
    WorkSheet.write(2,11,u"共用場所維持費",Style)
    WorkSheet.write(2,12,u"現金",Style)

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
    ('/sakura111/', MainHandler)
], debug=True)
