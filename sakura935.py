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

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    LblMsg = ""

    if self.request.get('BtnSAKURA930')  != '':
      self.redirect("/sakura930/")
      return

    if self.request.get('BtnKettei')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        self.DataDel()
        self.DataAdd()
        self.redirect("/sakura930/")
        return

    if self.request.get('Code') != '': # 初期表示→パラメタ取得
      CD = self.request.get('Code')
      cookieStr = 'Code=' + CD + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:    # ２回目からはクッキー取得
      CD = self.request.cookies.get('CD', '')

    DaiKubun,SyoKubun = CD.split("-")

    if  self.request.get('Code'): # 初回表示?
      Rec = self.DataGet(DaiKubun,SyoKubun)
    else:
      Rec = {}
      Rec['TxtDaikubun']  = self.request.get('TxtDaikubun')
      Rec['TxtSyokubun']  = self.request.get('TxtSyokubun')
      Rec['TxtNaiyo']     = self.request.get('TxtNaiyo')

    template_values = {'Rec':Rec,
                      'LblMsg':LblMsg}

    path = os.path.join(os.path.dirname(__file__), 'sakura935.html')
    self.response.out.write(template.render(path, template_values))

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if   self.request.get('TxtDaikubun').isdigit() == False:
      LblMsg = "大区分が数値として認識できません。"
    elif self.request.get('TxtSyokubun').isdigit() == False:
      LblMsg = "小区分が数値として認識できません。"
    elif self.request.get('TxtNaiyo') == "":
      LblMsg = "内容は必須です。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataGet(self,DaiKubun,SyoKubun):

    Rec = {}

    sql  = "SELECT * FROM MstKoumoku"
    sql += " where DaiKubun = " + DaiKubun
    sql += "  and  SyoKubun = " + SyoKubun

    SnapData = db.GqlQuery(sql)
    results = SnapData.fetch(1)
    for result in results:
      Rec['TxtDaikubun']   = result.DaiKubun
      Rec['TxtSyokubun']   = result.SyoKubun
      Rec['TxtNaiyo']      = result.Naiyo

    return Rec

  def DataDel(self):

    sql  = "SELECT * FROM MstKoumoku"
    sql += " where DaiKubun = " + self.request.get('TxtDaikubun') 
    sql += "  and  SyoKubun = " + self.request.get('TxtSyokubun')

    SnapData = db.GqlQuery(sql)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

    return

  def DataAdd(self):

    DynaData = MstKoumoku()
    DynaData.DaiKubun = int(self.request.get('TxtDaikubun'))
    DynaData.SyoKubun = int(self.request.get('TxtSyokubun'))
    DynaData.Naiyo    = self.request.get('TxtNaiyo')
    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/sakura935/', MainHandler)
], debug=True)
