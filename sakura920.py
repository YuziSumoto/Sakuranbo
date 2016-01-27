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

    if self.request.get('BtnSAKURA925')  != '': # 追加
      self.redirect("/sakura925/")
      return

    LblMsg = ""

    for param in self.request.arguments():
      if "BtnDel" in param:
        self.DataDel(param.replace("BtnDel",""))

    strTable  =  self.tableSet()

    template_values = {'strTable':strTable,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura920.html')
    self.response.out.write(template.render(path, template_values))

  def DataDel(self,Room):
    SnapData = db.GqlQuery("SELECT * FROM MstRoom where Room = " + Room)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

#  テーブルセット
  def tableSet(self):
    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstRoom Order by Room")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>" + str(RecMst.Room) + "</TD>" # 
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '" + u"削除" + "'"
      retStr += " name='BtnDel"
      retStr += str(RecMst.Room)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

app = webapp2.WSGIApplication([
    ('/sakura920/', MainHandler)
], debug=True)
