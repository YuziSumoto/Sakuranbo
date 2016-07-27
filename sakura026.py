#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

import datetime

from Mst import *
from Dat import *

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Nengetu = self.request.get('Nengetu')
    cookieStr = 'Nengetu=' + Nengetu + ';'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    Room = self.request.get('Room')
    cookieStr = 'Room=' + Room + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    LblMsg = ""

    Rec = self.DataGet(Nengetu,Room,0)

    template_values = {'Rec'   :Rec,
                       'StrKanzya'   : self.SetKanzya(Rec.KanzyaID),
                       'LblMsg': LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura026.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Nengetu = self.request.cookies.get('Nengetu', '')
    Room    = self.request.cookies.get('Room', '')

    if self.request.get('BtnSAKURA021')  != '':  # 中止
      self.redirect("/sakura021/?Nengetu=" + Nengetu )
      return

    LblMsg = ""
    LblMsg = self.request.get('KanzyaID')
    
    if self.request.get('BtnKettei')  != '':  # 決定
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        DatDenki().DelRec(Nengetu,Room)
        self.DataAdd(Nengetu,Room)
        self.redirect("/sakura021/?Nengetu=" + Nengetu )
        return

    Rec = {}
    ParaNames = self.request.arguments()
    for ParaName in ParaNames:
      Rec[ParaName]    = self.request.get(ParaName)
    Rec['Room']      = Room
    Rec = self.DataGet(Nengetu,Room,1)

    template_values = {'Rec'   :Rec,
                       'StrKanzya'   : self.SetKanzya(Rec.KanzyaID),
                       'LblMsg': LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura026.html')
    self.response.out.write(template.render(path, template_values))

  def DataGet(self,Nengetu,Room,Kubun):

    sql  = "SELECT * FROM DatDenki"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    Snap = db.GqlQuery(sql)
    if Snap.count() == 0:
      Rec = DatDenki()
      Rec.Room     = int(Room)
      Rec.KanzyaID = None
    else:
      Rec = Snap.fetch(1)[0]

    return Rec

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if self.request.get('KanzyaID') == "" or self.request.get('KanzyaID') == 0:
      LblMsg = "患者が指定されていません。"
    elif self.request.get('Kingaku') != ""  and self.request.get('Kingaku').isdigit() == False:
      LblMsg = "金額が数値として認識できません。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataAdd(self,Hizuke,Room):

    DynaData = DatDenki()
    DynaData.Hizuke = datetime.datetime.strptime(Hizuke + "/01", '%Y/%m/%d')
    DynaData.Room         = int(Room)
    DynaData.KanzyaID   =  int(self.request.get('KanzyaID'))
    DynaData.KanzyaName =  MstKanzya().GetKanzyaName(self.request.get('KanzyaID'))
    if  self.request.get('SMeter1') != "":
      DynaData.SMeter1        = float(self.request.get('SMeter1'))
    if  self.request.get('SMeter2') != "":
      DynaData.SMeter2        = float(self.request.get('SMeter2'))
    if  self.request.get('EMeter1') != "":
      DynaData.EMeter1        = float(self.request.get('EMeter1'))
    if  self.request.get('EMeter2') != "":
      DynaData.EMeter2        = float(self.request.get('EMeter2'))
 
    DynaData.KeisanKubun  = int(self.request.get('KeisanKubun'))
    DynaData.Comment      = self.request.get('Comment')
    if  self.request.get('Kingaku') != "":
      DynaData.Kingaku      = int(self.request.get('Kingaku'))

    DynaData.put()

    return

  def SetKanzya(self,KanzyaID):

    retStr = ""

    retStr += "<option value=0>&nbsp</option>"

    Snap = db.GqlQuery("SELECT * FROM MstKanzya Order by Kana")
    for Rec in Snap.fetch(Snap.count()):
      retStr += "<option value=" + str(Rec.KanzyaID) + " "
      if KanzyaID == Rec.KanzyaID:  # 選択判定
        retStr += " selected "
      retStr += ">"
      retStr += Rec.Name
      retStr += "</option>"

    return retStr

app = webapp2.WSGIApplication([
    ('/sakura026/', MainHandler)
], debug=True)
