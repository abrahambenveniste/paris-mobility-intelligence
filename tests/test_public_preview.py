import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from preview_server import preview_handler


class PublicPreviewTests(unittest.TestCase):
    def test_network_is_available_and_private_routes_are_not(self):
        network={'scope':'public_map_preview','routes':[{'name':'example'}],'stops':[{'name':'example'}]}
        server=ThreadingHTTPServer(('127.0.0.1',0),preview_handler(network))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            for path,status in [('/',200),('/api/network',200),('/public.js',200),('/.env',404),
                                ('/data/disruptions.sqlite',404),('/api/traffic',404),('/api/departures',404)]:
                connection=http.client.HTTPConnection('127.0.0.1',server.server_port)
                connection.request('GET',path);response=connection.getresponse();body=response.read()
                self.assertEqual(response.status,status)
                if path=='/api/network':self.assertEqual(json.loads(body),network)
                if path=='/':self.assertIn(b'Live arrivals, traffic notices and historical analysis are not available',body)
                connection.close()
        finally:
            server.shutdown();server.server_close();thread.join()
