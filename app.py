import chalice

app = chalice.Chalice(app_name='waypoint')


@app.route('/')
def index():
    return {'hello': 'world'}


# 06h00 ET
@app.schedule(chalice.Cron(minutes=0, hours=11, day_of_month='*', month='*', day_of_week='*', year='*'))
def refresh_data(event):
    pass
