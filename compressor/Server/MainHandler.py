import tornado.ioloop
import tornado.web
# import pydub

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        homePage = file.open("Interface.html","r")
        self.write(file.read(homePage))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888) # Listen on this port of 127.0.0.1
    tornado.ioloop.IOLoop.current().start()