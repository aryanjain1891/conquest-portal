"""
Populate the portal with realistic demo activity.

Idempotent where possible; safe to re-run. Creates:
  - MeetingSlot: next 14 days, weekday afternoons, for mentors/coaches/experts
  - MeetingRequest: mix of pending/accepted/declined between startups and slot owners
  - Connection: requests in various states between startups/mentors/alumni/experts
  - GlobalEvent: a handful of upcoming cohort events
  - Announcement: a few broadcast messages
  - Notification: per-user personalized messages

Run inside the web container:
  docker exec -w /home/app/web conquest_back_web python -m scripts.seed_activity
"""
import os, django, random
from datetime import timedelta, time as dtime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conquest_back.settings")
django.setup()

from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from users.models import UserProfile, Connection
from meetings.models import MeetingSlot, MeetingRequest, GlobalEvent
from staff.models import Notification, Announcement

SEED = 2026
random.seed(SEED)


def log(msg): print(msg, flush=True)


def users_by_role(role):
    """Return UserProfile instances matching this role (NOT User)."""
    return list(UserProfile.objects.filter(role__iexact=role))


def pick(xs, k=None):
    if k is None:
        return random.choice(xs) if xs else None
    if not xs:
        return []
    k = min(k, len(xs))
    return random.sample(xs, k)


def build_meeting_slots():
    """Each mentor/coach/expert gets ~4 available slots over the next 14 days, on weekday afternoons."""
    slot_owners = (users_by_role("Mentor") + users_by_role("Coach")
                   + users_by_role("Function Expert"))
    now = timezone.localtime()
    today = now.date()
    created = 0
    for u in slot_owners:
        for _ in range(random.randint(2, 5)):
            day_offset = random.randint(1, 14)
            day = today + timedelta(days=day_offset)
            # skip weekends
            if day.weekday() >= 5:
                day += timedelta(days=7 - day.weekday())
            hour = random.choice([10, 11, 14, 15, 16, 17, 18])
            start = timezone.make_aware(
                timezone.datetime.combine(day, dtime(hour, 0))
            )
            end = start + timedelta(minutes=random.choice([30, 45, 60]))
            # avoid exact duplicates
            if MeetingSlot.objects.filter(user=u, start_time=start).exists():
                continue
            MeetingSlot.objects.create(user=u, start_time=start, end_time=end, free=True)
            created += 1
    log(f"  MeetingSlot   · created {created}  · total now {MeetingSlot.objects.count()}")
    return slot_owners


def build_meeting_requests():
    startups = users_by_role("Startup")
    slots = list(MeetingSlot.objects.filter(free=True))
    if not startups or not slots:
        log("  MeetingRequest: skip (no startups or slots)")
        return
    created = 0
    # Each startup requests ~2-5 meetings
    for s in startups:
        picks = pick(slots, random.randint(2, 5))
        for slot in picks:
            status = random.choices(
                ["pending", "accepted", "declined"],
                weights=[5, 3, 1], k=1
            )[0]
            exists = MeetingRequest.objects.filter(requester=s, slot=slot).exists()
            if exists:
                continue
            MeetingRequest.objects.create(
                requester=s,
                requested=slot.user,
                slot=slot,
                slot_start_time=slot.start_time,
                slot_end_time=slot.end_time,
                status=status,
                meet_link="https://meet.example.com/demo" if status == "accepted" else "",
                cel_approved=(status == "accepted"),
            )
            if status == "accepted":
                slot.free = False
                slot.save(update_fields=["free"])
                slots.remove(slot)
            created += 1
    log(f"  MeetingRequest· created {created}  · total now {MeetingRequest.objects.count()}")


def build_connections():
    """Startups reach out to mentors/alumni/experts; a few alumni reach out to startups."""
    startups = users_by_role("Startup")
    mentors = users_by_role("Mentor")
    alumni = users_by_role("Alumni")
    experts = users_by_role("Function Expert")
    created = 0
    for s in startups:
        targets = pick(mentors + alumni + experts, random.randint(3, 7))
        for t in targets:
            if Connection.objects.filter(from_user=s, to_user=t).exists():
                continue
            approved = random.choice([True, True, False])
            accepted = approved and random.choice([True, False])
            Connection.objects.create(from_user=s, to_user=t,
                                      approved=approved, accepted=accepted)
            created += 1
    # some incoming requests from alumni to startups
    for a in alumni:
        targets = pick(startups, random.randint(1, 3))
        for t in targets:
            if Connection.objects.filter(from_user=a, to_user=t).exists():
                continue
            Connection.objects.create(from_user=a, to_user=t, approved=True, accepted=False)
            created += 1
    log(f"  Connection    · created {created}  · total now {Connection.objects.count()}")


def build_global_events():
    now = timezone.localtime()
    events = [
        ("Cohort Kickoff", "Welcome + program walkthrough. Attendance mandatory for founders.", 2, 18, 60),
        ("Fireside: Product-Market Fit", "Session with a successful founder on finding PMF.", 5, 17, 75),
        ("Fundraising Bootcamp", "Hands-on workshop covering seed round mechanics, term sheets, and investor outreach.", 9, 15, 120),
        ("Demo Day Dry Run", "Practice pitches in front of mentors; detailed feedback.", 14, 16, 90),
        ("Mentor Office Hours", "Open Q&A with a rotating mentor panel.", 18, 18, 60),
    ]
    created = 0
    for name, desc, day_offset, hour, mins in events:
        start = timezone.make_aware(
            timezone.datetime.combine(now.date() + timedelta(days=day_offset), dtime(hour, 0))
        )
        end = start + timedelta(minutes=mins)
        if GlobalEvent.objects.filter(name=name, slot_start_time=start).exists():
            continue
        GlobalEvent.objects.create(
            name=name, description=desc,
            slot_start_time=start, slot_end_time=end,
            meet_link="https://meet.example.com/cohort-event",
        )
        created += 1
    log(f"  GlobalEvent   · created {created}  · total now {GlobalEvent.objects.count()}")


def build_announcements():
    samples = [
        (["Startup"], "Weekly founder standup is on Friday 5pm. Bring your top two blockers."),
        (["Startup", "Mentor"], "Deck review session next week. Upload your latest deck by Wednesday."),
        (["Mentor", "Coach", "Function Expert"], "Slot submission window closes Saturday 11:59 PM."),
        (["Startup"], "Demo Day is in 4 weeks. Founders: book a mock-pitch slot this week."),
        (["Startup", "Alumni"], "Alumni mixer scheduled for next Thursday — RSVP inside the portal."),
    ]
    created = 0
    for roles, msg in samples:
        if Announcement.objects.filter(message=msg).exists():
            continue
        a = Announcement.objects.create(message=msg)
        try:
            a.roles = ",".join(roles)
            a.save()
        except Exception:
            pass
        created += 1
    log(f"  Announcement  · created {created}  · total now {Announcement.objects.count()}")


def build_notifications():
    """Small unread-notification buffer per profile so dashboards aren't empty."""
    samples = [
        "Welcome to the Conquest cohort portal!",
        "A new mentor just published their availability. Check the Mentors page.",
        "Your profile is 70% complete — add your USP to help with matching.",
        "Reminder: forms due by end of week.",
        "Demo Day pitch order announced — see the Events page.",
    ]
    created = 0
    users = list(UserProfile.objects.exclude(user__is_superuser=True).exclude(user__isnull=True))
    for u in users:
        # only add if user has fewer than 2 notifications
        if Notification.objects.filter(user=u).count() >= 2:
            continue
        msg = random.choice(samples)
        Notification.objects.create(user=u, message=msg, read=False)
        created += 1
    log(f"  Notification  · created {created}  · total now {Notification.objects.count()}")


def run():
    log("Seeding demo activity...")
    with transaction.atomic():
        build_meeting_slots()
        build_meeting_requests()
        build_connections()
        build_global_events()
        build_announcements()
        build_notifications()
    log("Done.")


if __name__ == "__main__":
    run()
