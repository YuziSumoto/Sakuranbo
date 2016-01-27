#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

from Mst import *
from Dat import *
import datetime

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnSAKURA000')  != '':
      self.redirect("/sakura000/")
      return

    if self.request.get('Nengetu') != '': # 初期表示→パラメタ取得
      Nengetu = self.request.get('Nengetu')
      cookieStr = 'Nengetu=' + Nengetu + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:    # ２回目からはクッキー取得
      Nengetu = self.request.cookies.get('Nengetu', '')

    if self.request.get('BtnSAKURA025')  != '':
      self.redirect("/sakura025/?Nengetu=" + Nengetu + "&Room=" + self.request.get('BtnSAKURA025') )
      return

    for param in self.request.arguments():
      if "BtnDel" in param:
        self.DataDel(Nengetu,param.replace("BtnDel",""))

    LblMsg    =  ""
    strTable  =  self.tableSet(Nengetu)  # 一覧セット

    PrintParam = "?LstDate="
    PrintParam += Nengetu

    template_values = {'strTable':strTable,
                       'PrintParam' : PrintParam,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura020.html')
    self.response.out.write(template.render(path, template_values))

#  テーブルセット(居室マスタ)
  def tableSet(self,Nengetu):

    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstRoom Order by Room")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"
      retStr += str(RecMst.Room)
      retStr += "' name='BtnSAKURA025"
      retStr += "'>"
      retStr += "</TD>"
      retStr += self.DataSet(Nengetu,str(RecMst.Room),RecYatinMst)
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '削除'"
      retStr += " name='BtnDel"
      retStr += str(RecMst.Room)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

#  テーブルセット（データ部)
  def DataSet(self,Nengetu,Room,RecYatinMst):

    retStr = ""

    WDatDenki = DatDenki()

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + Room

    SnapMst = db.GqlQuery(Sql)
  
    if SnapMst.count() == 0:
      for i in range(1,3):
        retStr += "<TD>&nbsp</TD>" # ＩＤ
    else:
      RecMst = SnapMst.fetch(1)
      retStr += "<TD>"  + str(RecMst[0].KanzyaID)    + "</TD>" # ＩＤ
      if RecMst[0].KanzyaName == None:
        retStr += "<TD>&nbsp</TD>" # 氏名
      else:
        retStr += "<TD>"  + RecMst[0].KanzyaName.encode('utf-8') + "</TD>" # 氏名

    Zengetu = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d') # 当月１日
    Zengetu -= datetime.timedelta(days=1) # 前月末日
    ZenMeter = WDatDenki.GetDenki(Zengetu.strftime('%Y/%m'),Room)

    KonMeter = WDatDenki.GetDenki(Nengetu,Room)
    if ZenMeter == 0 or ZenMeter == None:
      retStr += "<TD>&nbsp</TD>"
    else:
      retStr += "<TD align='right'>"  + ('%5.2f' % ZenMeter) + "</TD>" # 前月メータ
    if KonMeter == 0 or KonMeter ==None :
      retStr += "<TD>&nbsp</TD>"
    else:
      retStr += "<TD align='right'>"  + ('%5.2f' % KonMeter) + "</TD>" # 前月メータ

    if ZenMeter != None and KonMeter != None:
      Siyoryo = KonMeter - ZenMeter
    else:
      Siyoryo = 0

    if Siyoryo <= 0:
      retStr += "<TD>&nbsp</TD>"
    else:
      retStr += "<TD align='right'>"  + ('%5.2f' % Siyoryo) + "</TD>" # 当月使用数

    KeisanKubun,Comment,Kingaku = WDatDenki.GetKingaku(Nengetu,Room,RecYatinMst.DenkiTanka)

    retStr += "<TD align='right'>" # 計算額
    if KeisanKubun == 1:
      retStr += "手入力"
    else:
      retStr += "\\"  + ('%5.2f' % Kingaku)
    retStr += "</TD>"

    retStr += "<TD>"# コメント
    if Comment == None:
      retStr += "&nbsp"
    else:
      retStr += Comment.encode('utf-8')

    retStr += "</TD>"

    retStr += "<TD align='right'>\\"  + str(int(round(Kingaku,0))) + "</TD>"

    return retStr

  def DataDel(self,Nengetu,Room):
  
    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" +Nengetu.replace("/","-") + "-01')"
    Sql += " And   Room = " + Room

    SnapData = db.GqlQuery(Sql)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

    return

app = webapp2.WSGIApplication([
    ('/sakura020/', MainHandler)
], debug=True)
