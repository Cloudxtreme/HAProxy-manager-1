import web
import sys

urls = (
    '/(.*)', 'MainHandler'
)
app = web.application(urls, globals())


SERVER_NAME = sys.argv[1]


class MainHandler:
    """
        main handler class
    """

    def GET(self, name):
        """
            Get requests handler
        """
        return SERVER_NAME


if __name__ == "__main__":
    app.run()