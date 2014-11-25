#!/usr/bin/python

import SimpleHTTPServer, socket
import SocketServer

PORT = 8888

    
class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    Send the lat,lng values to the running emulator
    """
    def send_point_to_emulator(self,lat, lng):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5554))
        s.send("geo fix %s %s\nquit\n" % (lng, lat))
        s.close()
        
    '''For any GET request we write the HTML variable as a response'''
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(HTML))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(HTML)
        

    '''For any POST request we read the point and send it to the emulator'''
    def do_POST(self):
        data = self.rfile.readline()
        data = [float(x) for x in data.split()[1:]]        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()        
        self.send_point_to_emulator(data[0], data[1])
        
class WebServer(SocketServer.TCPServer):    
    allow_reuse_address = True
    
    def __init__(self,server_address):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandler)



HTML = """<!DOCTYPE html>
<html>
<head>
<style type="text/css">
html, body, #map-canvas {
    height: 100%;
    margin: 0;
    padding: 0;
}
</style>
<script type="text/javascript"
    src="https://maps.googleapis.com/maps/api/js?sensor=false">
</script>

<script type="text/javascript">
    var map,marker;
    
    function initialize() {
    
        var mapOptions = {
            center : {
                lat : -41.309573,
                lng : 174.784524
            },
            zoom : 18,
            mapTypeId: google.maps.MapTypeId.NORMAL,
            styles: []
        };
        
        map = new google.maps.Map(document.getElementById('map-canvas'),
                mapOptions);        
        marker = new google.maps.Marker({position:map.center,map:map});
        
        google.maps.event.addListener(map, 'click', function(x) {
            var pos = x.latLng;
            marker.setPosition(pos);
          var req = new XMLHttpRequest();        
          req.open('POST', 'http://localhost:8888', true);            
          req.send('location '+pos.lat()+' '+pos.lng()+'\\n');            
        });
}

google.maps.event.addDomListener(window, 'load', initialize);
</script>
</head>
<body>
    <div id="map-canvas"></div>
</body>
</html>
"""

httpd = WebServer(("localhost", PORT))
print "starting webserver at http://localhost:%d" % PORT
httpd.serve_forever()
