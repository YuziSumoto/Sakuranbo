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

    if self.request.get('Nengetu') != '': # 初期表示→パラメタ取得
      Nengetu = self.request.get('Nengetu')
      cookieStr = 'Nengetu=' + Nengetu + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
      Room = self.request.get('Room')
      cookieStr = 'Room=' + Room + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:    # ２回目からはクッキー取得
      Nengetu = self.request.cookies.get('Nengetu', '')
      Room    = self.request.cookies.get('Room', '')

    if self.request.get('BtnSAKURA020')  != '':  # 中止
      self.redirect("/sakura020/?Nengetu=" + Nengetu )
      return

    LblMsg = ""

    if self.request.get('BtnKettei')  != '':  # 決定
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        self.DataDel(Nengetu,Room)
        self.DataAdd(Nengetu,Room)
        self.redirect("/sakura020/?Nengetu=" + Nengetu )
        return

    Rec = {}
    ParaNames = self.request.arguments()
    for ParaName in ParaNames:
      Rec[ParaName]    = self.request.get(ParaName)
    Rec['TxtRoom']      = Room
    if Rec.has_key('OptKeisan') == False:
      Rec['OptKeisan0'] = "checked"
    elif Rec['OptKeisan']   == "0":
      Rec['OptKeisan0'] = "checked"
    else:
      Rec['OptKeisan1'] = "checked"

    if  self.request.get('Nengetu'): # 初回表示?
      Rec = self.DataGet(Rec,Nengetu,Room,0)
    else:
      Rec = self.DataGet(Rec,Nengetu,Room,1)

    template_values = {'Rec'   :Rec,
                       'LblMsg': LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura025.html')
    self.response.out.write(template.render(path, template_values))

  def DataGet(self,Rec,Nengetu,Room,Kubun):

    sql  = "SELECT * FROM DatMain"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    SnapData = db.GqlQuery(sql)
    results = SnapData.fetch(1)
    for result in results:
      Rec['TxtID']    = str(result.KanzyaID)
    if Rec.has_key('TxtID') == False:
      Rec['TxtName']    = ""
    elif Rec['TxtID'] != "":
      Rec['TxtName']    = MstKanzya().GetKanzyaName(Rec['TxtID'])

    Zengetu = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d') # 当月１日
    Zengetu -= datetime.timedelta(days=1) # 前月末日
    
    Rec['TxtZengetu']  = DatDenki().GetDenki(Zengetu.strftime('%Y/%m'),Room)
    
    if Kubun == 0:  # 初回表示時のみ
      Rec['TxtMeter']    = DatDenki().GetDenki(Nengetu,Room)
      RecMst = MstYatin().GetRec(Nengetu)
      KeisanKubun,Comment,Kingaku = DatDenki().GetKingaku(Nengetu,Room,RecMst.DenkiTanka)
      if KeisanKubun != 1:
        Rec['OptKeisan0']    = "Checked"
      else:
        Rec['OptKeisan1']    = "Checked"
      if Comment != None:
        Rec['TxtComment']    = Comment
      if Kingaku != None:
        Rec['TxtKingaku']    = str(int(Kingaku))

    return Rec

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if self.request.get('TxtMeter') != ""  and self.request.get('TxtMeter').replace(".","").isdigit() == False:
      LblMsg = "当月メータが数値として認識できません。"
    elif self.request.get('TxtKingaku') != ""  and self.request.get('TxtKingaku').isdigit() == False:
      LblMsg = "金額が数値として認識できません。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataDel(self,Nengetu,Room):

    sql  = "SELECT * FROM DatDenki"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    SnapData = db.GqlQuery(sql)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

  def DataAdd(self,Hizuke,Room):

    DynaData = DatDenki()
    DynaData.Hizuke = datetime.datetime.strptime(Hizuke + "/01", '%Y/%m/%d')
    DynaData.Room         = int(Room)
 
    if  self.request.get('TxtMeter') != "":
      DynaData.Meter        = float(self.request.get('TxtMeter'))
 
    DynaData.KeisanKubun  = int(self.request.get('OptKeisan'))
    DynaData.Comment      = self.request.get('TxtComment')
    if  self.request.get('TxtKingaku') != "":
      DynaData.Kingaku      = int(self.request.get('TxtKingaku'))

    DynaData.put()

    return


app = webapp2.WSGIApplication([
    ('/sakura025/', MainHandler)
], debug=True)
