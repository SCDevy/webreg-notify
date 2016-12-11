from app.factory import ApplicationFactory

app = ApplicationFactory().create(config_filename="config")
app.run()