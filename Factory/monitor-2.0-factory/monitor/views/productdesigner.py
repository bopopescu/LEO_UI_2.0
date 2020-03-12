from flask_restful import Resource
from flask import render_template, Response, session
from flask import jsonify
import LeoFlaskUtils

class productdesigner(Resource):
  def post(self):

      template = 'local/vendor/productdesigner.html'
      return render_template( template )
