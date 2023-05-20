from apscheduler.schedulers.background import BackgroundScheduler

from order.views import pending_order_assign


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(pending_order_assign, "interval", minutes=1, id="pending_order__001", replace_existing=True)
    scheduler.start()