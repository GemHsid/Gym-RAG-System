from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking

def update_course_booked_count(course):
    """
    Recalculate and update the booked_count for a course.
    """
    try:
        # Refresh course from db to ensure we have the latest data if needed, 
        # but here we just need the id to filter bookings.
        # Actually, counting bookings with status='booked' is the source of truth.
        count = Booking.objects.filter(course=course, status='booked').count()
        course.booked_count = count
        course.save(update_fields=['booked_count'])
    except Exception as e:
        # Log error or ignore if course is deleted
        print(f"Error updating course booked_count: {e}")

@receiver(post_save, sender=Booking)
def update_course_booked_count_on_save(sender, instance, **kwargs):
    if instance.course:
        update_course_booked_count(instance.course)

@receiver(post_delete, sender=Booking)
def update_course_booked_count_on_delete(sender, instance, **kwargs):
    if instance.course:
        update_course_booked_count(instance.course)
