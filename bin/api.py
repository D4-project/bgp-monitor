from flask import Flask
from flask_restx import fields, Api, Resource


class bgpapi():
    instance = None
    def __init__(self, graph):
        if instance is None:
            instance = Api(Flask(__name__))
        self.graph = graph


@bgpapi.instance.route('/get')
class bgp_monitor(Resource):
    def post(self):
        return {'hello': 'world'}

        if date:
            # retrieve graph earlier than date
            # retrieve records after this date
            # rebuild the whole graph using these records
            # 
            pass
        else:
            self.graph.get()
            # retrieve graph
            pass