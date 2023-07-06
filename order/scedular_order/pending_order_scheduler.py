from apscheduler.schedulers.background import BackgroundScheduler
from order.views import order_waiting, pending_order_assign
from upload_video.views import auto_watermark_make


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(pending_order_assign, "interval", minutes=30, id="pending_order__001", replace_existing=True)
    scheduler.add_job(order_waiting, "interval", minutes=30, id="waiting_order__001", replace_existing=True)
    scheduler.add_job(auto_watermark_make, "interval", minutes=15, id="auto_watermark__001", replace_existing=True)
    scheduler.start()