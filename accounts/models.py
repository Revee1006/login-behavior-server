from django.db import models

class LoginEvent(models.Model):
    event = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event} at {self.timestamp}"

class LoginBehavior(models.Model):
    session_id = models.CharField(max_length=100)
    timestamp_utc = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField()
    is_mobile_device = models.BooleanField(default=False)

    keystroke_counter = models.IntegerField(default=0)
    erase_keys_percentage = models.FloatField(default=0)
    press_press_average_interval = models.FloatField(default=0)
    word_counter = models.IntegerField(default=0)

    key_dwell_mean = models.FloatField(default=0)
    key_dwell_std = models.FloatField(default=0)
    key_dwell_median = models.FloatField(default=0)

    paste_events_count = models.IntegerField(default=0)
    copy_events_count = models.IntegerField(default=0)

    mouse_action_click_left = models.IntegerField(default=0)
    mouse_action_click_right = models.IntegerField(default=0)

    scroll_events_count = models.IntegerField(default=0)
    window_focus_changes = models.IntegerField(default=0)

    touch_events_count = models.IntegerField(default=0)
    touch_vs_mouse_ratio = models.FloatField(default=0)

    js_event_rate = models.IntegerField(default=0)

    def __str__(self):
        return self.session_id
