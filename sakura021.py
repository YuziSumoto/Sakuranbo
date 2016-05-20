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

  def get(self): # 初期表示

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Nengetu = self.request.get('Nengetu')
    cookieStr = 'Nengetu=' + Nengetu + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    LblMsg    =  ""
    strTable  =  self.tableSet(Nengetu)  # 一覧セット

    PrintParam = "?LstDate="
    PrintParam += Nengetu

    template_values = {'strTable':strTable,
                       'PrintParam' : PrintParam,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura021.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnSAKURA000')  != '':
      self.redirect("/sakura000/")
      return
    Nengetu = self.request.cookies.get('Nengetu', '')

    if self.request.get('BtnSAKURA026')  != '':
      self.redirect("/sakura026/?Nengetu=" + Nengetu + "&Room=" + self.request.get('BtnSAKURA026') )
      return

    for param in self.request.arguments():
      if "BtnDel" in param:
        self.DataDel(Nengetu,param.replace("BtnDel",""))

    LblMsg    =  ""
    strTable  =  self.tableSet(Nengetu)  # 一覧セット

    PrintParam = "?LstDate=" + Nengetu

    template_values = {'strTable':strTable,
                       'PrintParam' : PrintParam,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura021.html')
    self.response.out.write(template.render(path, template_values))

#  テーブルセット(居室マスタ)
  def tableSet(self,Nengetu):

    RecYatinMst = MstYatin().GetRec(Nengetu) # 家賃マスタ取得

    retStr = ""
    for Ctr in range(1,41):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"  + str(Ctr) + "'"
      retStr += " name='BtnSAKURA026'>"
      retStr += "</TD>"
      retStr += self.DataSet(Nengetu,str(Ctr),RecYatinMst)
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '削除'"
      retStr += " name='BtnDel" + str(Ctr) + "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

#  テーブルセット（データ部)
  def DataSet(self,Nengetu,Room,RecYatinMst):

    retStr = ""

    WDatDenki = DatDenki()

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + Room

    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0: # データ無し
      Rec = {}
      for i in range(1,3):
        retStr += "<TD>&nbsp</TD>" # ＩＤ
    else:
      Rec = SnapMst.fetch(1)[0]
      retStr += "<TD>"  + str(RecMst.KanzyaID)    + "</TD>" # ＩＤ
      if Rec.KanzyaName == None:
        retStr += "<TD>&nbsp</TD>" # 氏名
      else:
        retStr += "<TD>"  + RecMst.KanzyaName + "</TD>" # 氏名

    Siyoryo = 0
    for Ctr in range(1,3): # ２回ループ
      retStr += "<TD align='right'>" # 当月メータ
      if getattr(Rec,"SMeter" + str(Ctr),None) == None: # 未指定？
        retStr += "&nbsp"
      else:
        retStr += ('%5.2f' % getattr(Rec,"SMeter" + str(Ctr)))
      retStr += "</TD>" 
      retStr += "<TD align='right'>" # 前月メータ
      if getattr(Rec,"EMeter" + str(Ctr),None) == None:
        retStr += "&nbsp"
      else:
        retStr += ('%5.2f' % getattr(Rec,"EMeter" + str(Ctr)))
      retStr += "</TD>"
        
    retStr += "<TD align='right'>" # 使用量
    if getattr(Rec,"EMeter" + str(Ctr),None) == None: # None
      retStr += "&nbsp"
    else:
      retStr += ('%5.2f' % getattr(Rec,"EMeter" + str(Ctr)))
    retStr += "</TD>"

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
    ('/sakura021/', MainHandler)
], debug=True)
