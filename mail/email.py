
from django_mailbox.signals import message_received
from django.dispatch import receiver
from django.core.mail import EmailMessage, make_msgid
import logging
from mail.utils.inference import generate_response
from .models import Thread, Message
from django.utils import timezone

logger = logging.getLogger(__name__)

@receiver(message_received)
def auto_reply(sender, message, **kwargs):
    # message.from_address may be a list or a string
    raw_from = message.from_address
    if isinstance(raw_from, (list, tuple)):
        # grab the first valid address
        from_addr = raw_from[0]
    else:
        from_addr = raw_from

    # strip any stray whitespace/brackets
    from_addr = from_addr.strip().strip("[]")

    msg_id    = message.message_id or ""

    in_reply  = message.in_reply_to or ""
    subj      = message.subject or ""
    body_text = message.text or message.html or ""
    now       = timezone.now()

    if in_reply:
        try:
            parent = Message.objects.get(message_id=in_reply)
            thread = parent.thread
        except Message.DoesNotExist:
            thread = Thread.objects.create(thread_id=msg_id, subject=subj)
    else:
        thread = Thread.objects.create(thread_id=msg_id, subject=subj)
    
    Message.objects.create(
        thread       = thread,
        message_id   = msg_id,
        in_reply_to  = in_reply or None,
        from_address = from_addr,
        to_addresses = "voltwaydryft@gmail.com",
        subject      = subj,
        body         = body_text,
        direction    = Message.INBOUND,
        timestamp    = now,
    )

    reply_subject = "Re: " + (message.subject or "")
    reply_body = generate_response(f"From: {from_addr}\nSubject: {message.subject}\nBody: {body_text}")

    reply = EmailMessage(
        subject=reply_subject,
        body=reply_body,
        to=[from_addr],  # now a clean list of one real email string
        headers={
            "In-Reply-To": message.message_id or "",
            "References": message.message_id or "",
        },
    )

    try:
        reply.send(fail_silently=False)
        logger.info(f"Sent auto-reply to {from_addr}")
    except Exception:
        logger.exception(f"Failed sending auto-reply to {from_addr}")
    
    outgoing_msg_id = make_msgid()
    
    Message.objects.create(
        thread       = thread,
        message_id   = outgoing_msg_id,
        in_reply_to  = msg_id,
        from_address = "voltwaydryft@gmail.com",     # uses DEFAULT_FROM_EMAIL
        to_addresses = from_addr,
        subject      = reply_subject,
        body         = reply_body,
        direction    = Message.OUTBOUND,
        timestamp    = timezone.now(),
    )