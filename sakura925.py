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

    if self.request.get('BtnSAKURA920')  != '':
      self.redirect("/sakura920/")
      return

    if self.request.get('BtnKettei')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        self.DataDel()
        self.DataAdd()
        self.redirect("/sakura920/")
        return

    Rec = {}
    Rec['TxtRoom']  = self.request.get('TxtRoom')

    template_values = {'Rec':Rec,
                      'LblMsg':LblMsg}

    path = os.path.join(os.path.dirname(__file__), 'sakura925.html')
    self.response.out.write(template.render(path, template_values))

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if   self.request.get('TxtRoom').isdigit() == False:
      LblMsg = "居室番号が数値として認識できません。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataDel(self):
    SnapData = db.GqlQuery("SELECT * FROM MstRoom where Room = " + self.request.get('TxtRoom'))
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

  def DataAdd(self):

    DynaData = MstRoom()
    DynaData.Room = int(self.request.get('TxtRoom'))
    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/sakura925/', MainHandler)
], debug=True)
