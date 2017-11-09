from tornado import ioloop
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

# configure custom scripts here
def main():
    app = make_app()
    app.listen(8888)  # Listen on this port of 127.0.0.1
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main() # Calling a configured main function that will run everything that we need
