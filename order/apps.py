from django.apps import AppConfig


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order'

    def ready(self):
        print("Starting Scheduler ..")
        from order.scedular_order import pending_order_scheduler
        pending_order_scheduler.start()
