#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

from Mst import *
import datetime

#from dateutil import relativedelta

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnSAKURA910')  != '':
      self.redirect("/sakura910/")
      return

    if self.request.get('BtnKettei')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        self.DataDel()
        self.DataAdd()
        self.redirect("/sakura910/")
        return

    if self.request.get('KanzyaID') != '': # 初期表示→パラメタ取得
      KanzyaID = self.request.get('KanzyaID')
      cookieStr = 'KanzyaID=' + KanzyaID + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:    # ２回目からはクッキー取得
      KanzyaID = self.request.cookies.get('KanzyaID', '')

    if  self.request.get('KanzyaID'): # 初回表示?
      Rec = {}
      Rec = self.DataGet(KanzyaID)
    else:
      Rec = {}
      Rec['TxtKanzyaID']  = self.request.get('TxtKanzyaID')
      Rec['TxtName']      = self.request.get('TxtName')
      Rec['TxtKana']      = self.request.get('TxtKana')
      Rec['TxtSyozoku']   = self.request.get('TxtSyozoku')
      Rec['TxtBikou']     = self.request.get('TxtBikou')

    template_values = {'Rec':Rec,
                      'LblMsg':LblMsg}

    path = os.path.join(os.path.dirname(__file__), 'sakura915.html')
    self.response.out.write(template.render(path, template_values))

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if   self.request.get('TxtKanzyaID').isdigit() == False:
      LblMsg = "患者IDが数値として認識できません。"
    elif self.request.get('TxtName') == "":
      LblMsg = "氏名は必須です。"
    elif self.request.get('TxtKana') == "":
      LblMsg = "かな氏名は必須です。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataGet(self,KanzyaID):

    Rec = {}

    SnapData = db.GqlQuery("SELECT * FROM MstKanzya where KanzyaID = " + KanzyaID)
    results = SnapData.fetch(1)
    for result in results:
      Rec['TxtKanzyaID']   = result.KanzyaID
      Rec['TxtName']       = result.Name
      Rec['TxtKana']       = result.Kana
      Rec['TxtSyozoku']    = result.Syozoku
      Rec['TxtBikou']      = result.Bikou

    return Rec

  def DataDel(self):
    SnapData = db.GqlQuery("SELECT * FROM MstKanzya where KanzyaID = " + self.request.get('TxtKanzyaID'))
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

  def DataAdd(self):

    DynaData = MstKanzya()
    DynaData.KanzyaID = int(self.request.get('TxtKanzyaID'))
    DynaData.Name = self.request.get('TxtName')
    DynaData.Kana = self.request.get('TxtKana')
    DynaData.Syozoku = self.request.get('TxtSyozoku')
    DynaData.Bikou = self.request.get('TxtBikou')
    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/sakura915/', MainHandler)
], debug=True)
