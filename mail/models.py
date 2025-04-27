from django.db import models

class Thread(models.Model):
    """
    Represents a conversation, keyed off the first Message-ID seen.
    """
    thread_id  = models.CharField(max_length=255, unique=True)
    subject    = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.thread_id})"


class Message(models.Model):
    """
    A single email in or out.
    """
    INBOUND  = "in"
    OUTBOUND = "out"
    DIRECTION_CHOICES = [
        (INBOUND,  "Inbound"),
        (OUTBOUND, "Outbound"),
    ]

    thread       = models.ForeignKey(Thread,
                                     related_name="messages",
                                     on_delete=models.CASCADE)
    message_id   = models.CharField(max_length=255, unique=True)
    in_reply_to  = models.CharField(max_length=255, blank=True, null=True)
    from_address = models.CharField(max_length=255)
    to_addresses = models.TextField(blank=True)
    subject      = models.CharField(max_length=255, blank=True)
    body         = models.TextField(blank=True)
    direction    = models.CharField(max_length=3,
                                    choices=DIRECTION_CHOICES)
    timestamp    = models.DateTimeField()

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"[{self.get_direction_display()}] {self.from_address} @ {self.timestamp}"