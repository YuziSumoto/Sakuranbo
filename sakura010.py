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

    if self.request.get('BtnSAKURA015')  != '':
      self.redirect("/sakura015/?Nengetu=" + Nengetu + "&Room=" + self.request.get('BtnSAKURA015'))
      return

    for param in self.request.arguments():
      if "BtnDel" in param:
        self.DataDel(Nengetu,param.replace("BtnDel",""))

    if self.request.get('BtnFukusya')  != '':
      self.Fukusya(Nengetu)

    LblMsg    =  ""
    strTable  =  self.tableSet(Nengetu)

    PrintParam = "?LstDate="
    PrintParam += Nengetu

    template_values = {'strTable':strTable,
                       'PrintParam' : PrintParam,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura010.html')
    self.response.out.write(template.render(path, template_values))

#  テーブルセット(居室マスタ)
  def tableSet(self,Nengetu):

    RecYatinMst = MstYatin().GetRec(Nengetu)
    RecNyutai   = MstKoumoku().GetNyutai()

    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstRoom Order by Room")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"
      retStr += str(RecMst.Room)
      retStr += "' name='BtnSAKURA015"
      retStr += "'>"
      retStr += "</TD>"
      retStr += self.DataSet(Nengetu,str(RecMst.Room),RecYatinMst,RecNyutai)
   
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '削除'"
      retStr += " name='BtnDel"
      retStr += str(RecMst.Room)
      retStr += "'>"
      retStr += "</TD>"

      retStr += "</TR>"
    return retStr

#  テーブルセット（データ部)
  def DataSet(self,Nengetu,Room,RecYatinMst,RecNyutai):

    retStr = ""

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + Room

    SnapMst = db.GqlQuery(Sql)
  
    if SnapMst.count() == 0:
      for i in range(1,3):
        retStr += "<TD>&nbsp</TD>" # ＩＤ
      retStr += "<TD>空室</TD>" # ＩＤ
      for i in range(4,11):
        retStr += "<TD>&nbsp</TD>" # ＩＤ
    else:
      RecMst = SnapMst.fetch(1)
      retStr += "<TD>"  + str(RecMst[0].KanzyaID)    + "</TD>" # ＩＤ
      retStr += "<TD>" # 氏名
      if RecMst[0].KanzyaName == None:
        retStr += "&nbsp"
      else:
        retStr += RecMst[0].KanzyaName.encode('utf_8')
      retStr += "</TD>"

      retStr += "<TD>" # 入退区分
      if RecMst[0].IONaiyo == None:
        retStr += "&nbsp"
      else:
        retStr += RecMst[0].IONaiyo.encode('utf_8')
      retStr += "</TD>"

      retStr += "<TD>"  + RecMst[0].Zyokyo.encode('utf_8')      + "</TD>" # 状況
      retStr += "<TD align='right'>" # 入居日数
      if RecMst[0].Nissu != 0:
        retStr +=  str(RecMst[0].Nissu)       + "</TD>" # 入居日数
      retStr += "</TD>" 
      Yatin,Kyoeki,Kanri = DatMain().GetKingaku(Nengetu,RecMst[0],RecYatinMst)
      retStr += "<TD align='right'>\\"  + str(Yatin)  + "</TD>" # 家賃
      retStr += "<TD align='right'>\\"  + str(Kyoeki) + "</TD>" # 共益費
      retStr += "<TD align='right'>\\"  + str(Kanri)  + "</TD>" # 管理費
      retStr += "<TD>"  + RecMst[0].Biko.encode('utf_8')        + "</TD>" # 備考
      retStr += "<TD>"
      if  RecMst[0].GenkinFlg == 1:
        retStr += "○"
      retStr += "</TD>" # 現金フラグ

    return retStr

#  前月複写
  def Fukusya(self,Nengetu):

    Zengetu = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d') # 当月１日
    Zengetu -= datetime.timedelta(days=1) # 前月末日
    Zengetu = Zengetu.strftime('%Y/%m')

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" +Nengetu.replace("/","-") + "-01')"
#    Sql += " Where Hizuke = Date('" +Zengetu.replace("/","-") + "-01')"

    SnapData = db.GqlQuery(Sql)
    results = SnapData.fetch(100)
    for result in results:
      result.delete()

    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" + Zengetu.replace("/","-") + "-01')"
#    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"

    SnapMst = db.GqlQuery(Sql)
    RecMst = SnapMst.fetch(100)
    
    for Rec in RecMst:
      DynaData = DatMain()
      DynaData.Hizuke = datetime.datetime.strptime(Nengetu + '/01', '%Y/%m/%d')
#      DynaData.Hizuke = datetime.datetime.strptime(Zengetu + '/01', '%Y/%m/%d')
      DynaData.Room        = Rec.Room
      DynaData.KanzyaID    = Rec.KanzyaID
      DynaData.KanzyaName  = Rec.KanzyaName
      DynaData.IOKubun     = Rec.IOKubun
      DynaData.IONaiyo     = Rec.IONaiyo
      DynaData.Zyokyo      = Rec.Zyokyo
      DynaData.Nissu       = Rec.Nissu
      DynaData.GenkinFlg   = Rec.GenkinFlg
      DynaData.Biko        = Rec.Biko
      DynaData.put()

    return

  def DataDel(self,Nengetu,Room):
  
    Sql =  "SELECT * FROM DatMain"
    Sql += " Where Hizuke = Date('" +Nengetu.replace("/","-") + "-01')"
    Sql += " And   Room = " + Room

    SnapData = db.GqlQuery(Sql)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

app = webapp2.WSGIApplication([
    ('/sakura010/', MainHandler)
], debug=True)
