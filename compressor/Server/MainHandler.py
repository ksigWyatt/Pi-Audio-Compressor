import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        homePage = open("Interface.html", "r")
        htmlCode = homePage.read()
        self.write(htmlCode)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888) # Listen on this port of 127.0.0.1
    tornado.ioloop.IOLoop.current().start()




