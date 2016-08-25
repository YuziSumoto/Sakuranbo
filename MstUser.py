# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class MstUser(db.Model):
  Name              = db.StringProperty(multiline=False)      # ユーザ名

  def ChkUser(self,Name):


    Sql  =  "SELECT * FROM MstUser"
    Query = db.GqlQuery(Sql)
    Snap = Query.fetch(Query.count())

    if Query.count() == 0:
      Rec = MstUser()
      Rec.Name = " "
      Rec.put()
      return True

    RetFlg = False

    for Rec in Snap:
      if Rec.Name == Name:
        RetFlg = True
        break

    return RetFlg

