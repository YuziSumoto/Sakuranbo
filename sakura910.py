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

    if self.request.get('BtnSAKURA915')  != '': # 追加
      self.redirect("/sakura915/" + "?KanzyaID=0")
      return

    LblMsg = ""

    for param in self.request.arguments():
      if "BtnSAKURA915" in param:
        self.redirect("/sakura915/" + "?KanzyaID=" + param.replace("BtnSAKURA915",""))
        return

      if "BtnDel" in param:
        self.DataDel(param.replace("BtnDel",""))

    strTable  =  self.tableSet()

    template_values = {'strTable':strTable,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura910.html')
    self.response.out.write(template.render(path, template_values))

  def DataDel(self,KanzyaID):
    SnapData = db.GqlQuery("SELECT * FROM MstKanzya where KanzyaID = " + KanzyaID)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

#  テーブルセット
  def tableSet(self):
    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstKanzya Order by KanzyaID")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"
      retStr += "{0:08d}".format(RecMst.KanzyaID)
      retStr += "' name='BtnSAKURA915"
      retStr += str(RecMst.KanzyaID)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "<TD>" + RecMst.Name + "</TD>" # 氏名
      retStr += "<TD>" + RecMst.Kana + "</TD>" # かな氏名
      retStr += "<TD>" + RecMst.Syozoku + "</TD>" # 所属
      retStr += "<TD>" + RecMst.Bikou + "</TD>" # 備考
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '" + u"削除" + "'"
      retStr += " name='BtnDel"
      retStr += str(RecMst.KanzyaID)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

app = webapp2.WSGIApplication([
    ('/sakura910/', MainHandler)
], debug=True)
