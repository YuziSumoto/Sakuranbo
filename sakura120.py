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

    WorkBook =  self.TableDataSet(self.request.get('LstDate'),int(self.request.get('Kubun')) - 1)

    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.headers['Content-disposition'] = 'attachment; filename="sakura120.xls"'

    WorkBook.save(self.response.out)

  def TableDataSet(self,Nengetu,Kubun):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    SheetName = [u"家賃",u"管理費",u"電気代"]

    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得
    WDatMain  =  DatMain()
    WDatDenki =  DatDenki()

    WorkSheet = WorkBook.add_sheet(SheetName[Kubun])  # 新規Excelシート
    self.SetPrintParam(WorkSheet)  # 用紙サイズ等セット

    self.SetColSize(WorkSheet)        # 行,列サイズセット

    for i in range(0,2):
      RowOffset = i * 40
      self.SetRowSize(WorkSheet,RowOffset) # 行,列サイズセット
      self.SetTitle(WorkSheet,RowOffset)   # 固定部分セット

    self.SetData(WorkSheet,Kubun,WDatMain,WDatDenki,RecYatinMst)

    return  WorkBook

  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定

    WorkSheet.set_paper_size_code(13) # B5
    WorkSheet.set_portrait(0) # 横
    WorkSheet.top_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
    WorkSheet.fit_num_pages = 2
    return

  def SetData(self,WorkSheet,Kubun,WDatMain,WDatDenki,RecYatinMst):  # データセット

    Nengetu = self.request.get('LstDate')

#    Sql =  "SELECT * FROM  MstRoom"
#    Sql += " Where Room <= 100"
#    Sql += " Order by Room"
#    SnapMst = db.GqlQuery(Sql)
    OutRow = 5

    OutRec = 0
    RecCtr = 40  #SnapMst.count()
#    RecMst = SnapMst.fetch(RecCtr)
    

    Soukei = 0
    
    PageOffset = [0,0,40]
    ColOffset  = [0,11,0]

    Style = self.SetStyle(True,True,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    Style2 = self.SetStyle(True,False,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    Style3 = self.SetStyle(False,True,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    font = xlwt.Font() # Create the Font
    font.height = 120
    Style3.font = font

    Style4 = self.SetStyle(False,True,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    Style5 = self.SetStyle(False,True,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_RIGHT)

    for Page in range(0,3): # ３ページ
      PageKei = 0

      for RowCtr in range(0,17): # 各ページ17明細

        OutRec += 1
        while OutRec <= RecCtr: # 出力対象判定
#          ID,Kingaku = self.GetData(Nengetu,RecMst[OutRec - 1].Room,Kubun,WDatMain,WDatDenki,RecYatinMst)
          ID,Kingaku = self.GetData(Nengetu,OutRec,Kubun,WDatMain,WDatDenki,RecYatinMst)
          if ID != "" and Kingaku !="" and Kingaku != 0:
            break
          OutRec += 1
      
        OutRow = PageOffset[Page] +  5 + RowCtr * 2
#        OutRec += 1
        Honzitu = datetime.datetime.now().strftime('%m/%d')
        Tyousu1 = u"さくらんぼ"
        ymd = Nengetu.split("/")
        if   Kubun == 0:
          Tyousu2 = ymd[1] + u"月分家賃・共益費"
        elif Kubun == 1:
          Tyousu2 = ymd[1] + u"月分管理費"
        else:
          Tyousu2 = ymd[1] + u"月分電気代"

        Tyousu3 = ""
        if OutRec <= RecCtr:
#          ID,Kingaku = self.GetData(Nengetu,RecMst[OutRec - 1].Room,Kubun,WDatMain,WDatDenki,RecYatinMst)
          if Kingaku !="":
            PageKei += int(Kingaku)
          if OutRow != 5 and OutRow != 45: # 各ページ先頭行以外
            Honzitu = u"〃"
            Tyousu1 = u""
            Tyousu2 = u"〃"
          WorkSheet.write_merge(OutRow,1 + OutRow,ColOffset[Page] ,ColOffset[Page],Honzitu,Style)
#          Room = str(RecMst[OutRec - 1].Room)
          Room = str(OutRec)
        else:
          ID = ""
          Kingaku = 0  # 金額
          Tyousu1 = ""
          Tyousu2 = ""
          Room = "None"
          WorkSheet.write_merge(OutRow,1 + OutRow,ColOffset[Page] ,ColOffset[Page]," ",Style)

        WorkSheet.write_merge(OutRow,OutRow + 1,1 + ColOffset[Page] ,2 + ColOffset[Page],ID,Style)  # 患者ID

        if Room == "None":
          WorkSheet.write_merge(OutRow,OutRow + 1,3 + ColOffset[Page] ,4 + ColOffset[Page],u" ",Style2)  # 部屋マスタなし
        elif ID == "":
          WorkSheet.write_merge(OutRow,OutRow + 1,3 + ColOffset[Page] ,4 + ColOffset[Page],u"空室(" + Room + ")",Style2)  # 空室
        else:
          WorkSheet.write_merge(OutRow,OutRow + 1,3 + ColOffset[Page] ,4 + ColOffset[Page],MstKanzya().GetKanzyaName(ID),Style2)  # 患者名/

#        WorkSheet.write_merge(OutRow + 1,OutRow + 1,3 + ColOffset[Page] ,4 + ColOffset[Page],Room,Style5)  # 部屋番号

        WorkSheet.write_merge(OutRow,OutRow,5 + ColOffset[Page] ,6 + ColOffset[Page],Tyousu1,Style2)

        if Tyousu2 == u"〃":
          WorkSheet.write_merge(OutRow + 1,OutRow + 1,5 + ColOffset[Page] ,6 + ColOffset[Page],Tyousu2,Style4)
        else:
          WorkSheet.write_merge(OutRow + 1,OutRow + 1,5 + ColOffset[Page] ,6 + ColOffset[Page],Tyousu2,Style3)

        if int(Kingaku) ==0:
          WorkSheet.write_merge(OutRow,OutRow + 1,7 + ColOffset[Page] ,8 + ColOffset[Page],"",Style) # 金額
        else:
          WorkSheet.write_merge(OutRow,OutRow + 1,7 + ColOffset[Page] ,8 + ColOffset[Page],'{:,d}'.format(int(Kingaku)),Style) # 金額

      WorkSheet.write_merge(OutRow+2,OutRow+2,0 + ColOffset[Page] ,6 + ColOffset[Page],u"合計",Style) # 金額

      if PageKei ==0:
        WorkSheet.write_merge(OutRow+2,OutRow+2,7 + ColOffset[Page] ,8 + ColOffset[Page],"",Style) # 金額
      else:
        WorkSheet.write_merge(OutRow+2,OutRow+2,7 + ColOffset[Page] ,8 + ColOffset[Page],'{:,d}'.format(int(PageKei)),Style) # 金額


      Soukei += PageKei

    WorkSheet.write(2,8 ,u"３枚合計",Style2)
    WorkSheet.write(3,8 ,u"￥" + '{:,d}'.format(int(Soukei)),Style5)

    return

  def GetData(self,Nengetu,Room,Kubun,WDatMain,WDatDenki,RecYatinMst):  # セルスタイルセット

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + str(Room)

    SnapDat = db.GqlQuery(Sql)
  
    if SnapDat.count() == 0:
      return ("",0)

    SnapRec = SnapDat.fetch(1)[0]
    ID = SnapRec.KanzyaID
    if SnapRec.GenkinFlg == 1: # 現金フラグが立ってる人は０円
      Kingaku = 0
    elif Kubun == 0:     # 家賃
      Hozyo,Yatin,Kyoeki,Kanri =  WDatMain.GetKingaku(Nengetu,SnapRec,RecYatinMst)
      Kingaku = Yatin + Kyoeki
    elif Kubun == 1:   # 管理費
      Hozyo,Yatin,Kyoeki,Kanri =  WDatMain.GetKingaku(Nengetu,SnapRec,RecYatinMst)
      Kingaku = Kanri
    else:              # 電気代
      KeisanKubun,Comment,Kingaku = WDatDenki.GetKingaku(Nengetu,SnapRec.Room,RecYatinMst.DenkiTanka)
      Kingaku = int(round(Kingaku,0))

    return (ID,Kingaku)

  def SetStyle(self,Top,Bottom,Right,Left,Vert,Horz):  # セルスタイルセット

    Style = xlwt.XFStyle()
    Border = xlwt.Borders()
    if Top == True:
      Border.top     = xlwt.Borders.THIN
    if Bottom == True:
      Border.bottom  = xlwt.Borders.THIN
    if Left == True:
      Border.left    = xlwt.Borders.THIN
    if Right == True:
      Border.right   = xlwt.Borders.THIN

    Style.borders = Border
    
    Alignment      = xlwt.Alignment()

    if Vert != False:
      Alignment.vert = Vert
    if Horz != False:
      Alignment.horz = Horz

    Style.alignment = Alignment

    return Style

  def SetColSize(self,WorkSheet):  # 行,列サイズセット

    ColWidth = ["列の幅",5,3,3,5,5,3,5,3,6,1,1]
    for i in range(1,12):
      WorkSheet.col(i - 1).width = int(ColWidth[i] * 400)
      WorkSheet.col(i - 1 + 11).width = int(ColWidth[i] * 400)

    return
  def SetRowSize(self,WorkSheet,RowOffset):  # 行,列サイズセット

    for i in range(0,2):
      RowOffset = i * 40
      WorkSheet.row( 0 + RowOffset ).height_mismatch = 1
      WorkSheet.row( 0 + RowOffset ).height = int(10 * 20)

      WorkSheet.row( 1 + RowOffset ).height_mismatch = 1
      WorkSheet.row( 1 + RowOffset ).height = int(10 * 20)

      WorkSheet.row( 2 + RowOffset ).height_mismatch = 1
      WorkSheet.row( 2 + RowOffset ).height = int(20 * 20)

      WorkSheet.row( 3 + RowOffset ).height_mismatch = 1
      WorkSheet.row( 3 + RowOffset ).height = int(20 * 20)

      for j in range(0,36):
        WorkSheet.row( 4 + j + RowOffset ).height_mismatch = 1
        WorkSheet.row( 4 + j+ RowOffset ).height = int(12 * 20)

    return

  def SetTitle(self,WorkSheet,RowOffset):  # 固定部分セット

    if RowOffset == 0:
      MaxRange = 2
    else:
      MaxRange = 1

    Style = self.SetStyle(True,True,True,True,xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    for i in range(0,MaxRange):
      ColOffset = i * 11
      # TBRLVH

      WorkSheet.write_merge(1 + RowOffset,1 + RowOffset,0 + ColOffset ,1 + ColOffset,u"確認印",Style)
      WorkSheet.write_merge(1 + RowOffset,1 + RowOffset,2 + ColOffset ,3 + ColOffset,u"事務受付",Style)
      WorkSheet.write_merge(1 + RowOffset,1 + RowOffset,4 + ColOffset ,5 + ColOffset,u"扱者印",Style)
      WorkSheet.write_merge(1 + RowOffset,1 + RowOffset,6 + ColOffset ,7 + ColOffset,u"患者印",Style)

      WorkSheet.write_merge(2 + RowOffset,3 + RowOffset,0 + ColOffset ,1 + ColOffset," ",Style)
      WorkSheet.write_merge(2 + RowOffset,3 + RowOffset,2 + ColOffset ,3 + ColOffset," ",Style)
      WorkSheet.write_merge(2 + RowOffset,3 + RowOffset,4 + ColOffset ,5 + ColOffset," ",Style)
      WorkSheet.write_merge(2 + RowOffset,3 + RowOffset,6 + ColOffset ,7 + ColOffset," ",Style)

      WorkSheet.write(4 + RowOffset,0 + ColOffset,u"月日"   ,Style)
      WorkSheet.write_merge(4 + RowOffset,4 + RowOffset,1 + ColOffset ,2 + ColOffset,u"ＩＤ",Style)
      WorkSheet.write_merge(4 + RowOffset,4 + RowOffset,3 + ColOffset ,4 + ColOffset,u"氏名",Style)
      WorkSheet.write_merge(4 + RowOffset,4 + RowOffset,5 + ColOffset ,6 + ColOffset,u"丁数",Style)
      WorkSheet.write_merge(4 + RowOffset,4 + RowOffset,7 + ColOffset ,8 + ColOffset,u"金額",Style)

    return

app = webapp2.WSGIApplication([
    ('/sakura120/', MainHandler)
], debug=True)
