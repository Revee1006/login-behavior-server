from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from shop.models import Order
from django.http import JsonResponse
from django.conf import settings

import json
import statistics
import csv
import os
from datetime import datetime

from .models import LoginEvent
from .models import LoginBehavior

# =========================
# CSV SCHEMA (FROZEN)
# =========================

CSV_HEADERS = [
    "session_id",
    "timestamp_utc",
    "user_agent",
    "is_mobile_device",

    "keystroke_counter",
    "erase_keys_percentage",
    "press_press_average_interval",
    "word_counter",

    "key_dwell_mean",
    "key_dwell_std",
    "key_dwell_median",

    "flight_time_mean",
    "flight_time_std",

    "typing_burst_count",
    "paste_events_count",
    "copy_events_count",
    "modifier_key_usage_ratio",

    "mouse_action_click_left",
    "mouse_action_click_right",
    "mouse_click_interarrival_mean",
    "mouse_click_interarrival_std",
    "mouse_average_movement_speed",
    "mouse_path_smoothness",
    "mouse_jitter_std",

    "touch_events_count",
    "touch_vs_mouse_ratio",

    "scroll_events_count",
    "scroll_speed_mean",
    "scroll_speed_std",

    "element_hover_time_mean",
    "element_hover_time_std",

    "page_dwell_seconds",
    "form_focus_ratio",
    "js_event_rate",
    "window_focus_changes",
    "click_depth",

    "received_bytes",
    "sent_bytes",
    "http_status_error_rate",
    "requests_like_new_connections",
    "geo_ip_change_flag",
    "user_agent_variability_flag",
]


# =========================
# CSV WRITER
# =========================

def append_to_csv(row_data):
    csv_path = os.path.join(settings.BASE_DIR, "login_behavior.csv")
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row_data)


# =========================
# EXISTING AUTH VIEWS
# =========================

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('product_list')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
            )
            if user:
                login(request, user)
                return redirect('product_list')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('product_list')

# =========================
# STEP 3 + STEP 4 PIPELINE
# =========================

@csrf_exempt
def collect_raw_login_data(request):
    if request.method != "POST":
        return JsonResponse({"status": "ignored"}, status=405)

    try:
        raw_body = request.body.decode("utf-8")
        payload = json.loads(raw_body)
    except Exception as e:
        print("Beacon parse error:", e)
        return JsonResponse({"status": "bad_payload"}, status=400)

    features = extract_features(
        payload.get("keyboard", []),
        payload.get("mouse", []),
        payload.get("scroll", []),
        payload.get("focus", []),
        payload.get("clipboard", []),
        payload.get("touch", []),
    )

    row = {key: 0 for key in CSV_HEADERS}
    row.update(features)

    row["session_id"] = payload.get("session_id")
    row["timestamp_utc"] = datetime.utcnow().isoformat()
    row["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
    row["is_mobile_device"] = "Mobile" in row["user_agent"]

    append_to_csv(row)

    print("CSV ROW SAVED:", row["session_id"])

    LoginBehavior.objects.create(
        session_id=row["session_id"],
        timestamp_utc=row["timestamp_utc"],
        user_agent=row["user_agent"],
        is_mobile_device=row["is_mobile_device"],

        keystroke_counter=row["keystroke_counter"],
        erase_keys_percentage=row["erase_keys_percentage"],
        press_press_average_interval=row["press_press_average_interval"],
        word_counter=row["word_counter"],

        key_dwell_mean=row["key_dwell_mean"],
        key_dwell_std=row["key_dwell_std"],
        key_dwell_median=row["key_dwell_median"],

        paste_events_count=row["paste_events_count"],
        copy_events_count=row["copy_events_count"],

        mouse_action_click_left=row["mouse_action_click_left"],
        mouse_action_click_right=row["mouse_action_click_right"],

        scroll_events_count=row["scroll_events_count"],
        window_focus_changes=row["window_focus_changes"],
        touch_events_count=row["touch_events_count"],
        touch_vs_mouse_ratio=row["touch_vs_mouse_ratio"],

        js_event_rate=row["js_event_rate"],
    )
    
    return JsonResponse({"status": "saved"})


# =========================
# FEATURE EXTRACTION LOGIC
# =========================

def extract_features(keyboard, mouse, scroll, focus, clipboard, touch):
    features = {}

    keydowns = [e for e in keyboard if e.get("type") == "keydown"]
    keyups = [e for e in keyboard if e.get("type") == "keyup"]

    features["keystroke_counter"] = len(keydowns)

    erase = [
        e for e in keydowns
        if e.get("key") in ("Backspace", "Delete")
    ]
    features["erase_keys_percentage"] = (
        len(erase) / len(keydowns) if keydowns else 0
    )

    times = [e.get("time") for e in keydowns if e.get("time") is not None]
    intervals = [
        times[i+1] - times[i]
        for i in range(len(times)-1)
        if times[i+1] >= times[i]
    ]
    features["press_press_average_interval"] = (
        statistics.mean(intervals) if intervals else 0
    )

    features["word_counter"] = (
        len([e for e in keydowns if e.get("key") == " "]) + 1
        if keydowns else 0
    )

    dwell = []
    for kd in keydowns:
        kd_time = kd.get("time")
        kd_code = kd.get("code")
        if kd_time is None or kd_code is None:
            continue

        ku = next(
            (u for u in keyups
             if u.get("code") == kd_code and u.get("time", -1) >= kd_time),
            None
        )
        if ku:
            dwell.append(ku["time"] - kd_time)

    features["key_dwell_mean"] = statistics.mean(dwell) if dwell else 0
    features["key_dwell_std"] = statistics.stdev(dwell) if len(dwell) > 1 else 0
    features["key_dwell_median"] = statistics.median(dwell) if dwell else 0

    features["paste_events_count"] = len(
        [c for c in clipboard if c.get("type") == "paste"]
    )
    features["copy_events_count"] = len(
        [c for c in clipboard if c.get("type") == "copy"]
    )

    clicks = [e for e in mouse if e.get("type") == "click"]
    features["mouse_action_click_left"] = len(
        [c for c in clicks if c.get("button") == 0]
    )
    features["mouse_action_click_right"] = len(
        [c for c in clicks if c.get("button") == 2]
    )

    features["scroll_events_count"] = len(scroll)
    features["window_focus_changes"] = len(focus)
    features["touch_events_count"] = len(touch)
    features["touch_vs_mouse_ratio"] = (
        len(touch) / len(mouse) if mouse else 0
    )

    total = (
        len(keyboard) +
        len(mouse) +
        len(scroll) +
        len(focus) +
        len(clipboard) +
        len(touch)
    )
    features["js_event_rate"] = total

    return features