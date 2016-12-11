from flask import Flask

class ApplicationFactory(object):
    def create(self, config_filename=""):
        app = Flask(__name__)
        
        if config_filename != "":
            app.config.from_object(config_filename)

        from controller import enrollment
        app.register_blueprint(enrollment)
        
        return app