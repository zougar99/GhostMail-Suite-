# ─── Email Templates ──────────────────────────────────────────────────────────
# Each template is a function that returns (subject, html_body).
# The {offer_link} placeholder will be replaced with your actual CPA link.
# ──────────────────────────────────────────────────────────────────────────────


def template_airbnb_reward(offer_link, recipient_email=""):
    """Airbnb $750 reward template - clean and professional."""

    subject = "You've been selected - Claim your $750 Airbnb Credit!"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, Helvetica, sans-serif;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4; padding:20px 0;">
<tr>
<td align="center">

<!-- Main Container -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.1);">

<!-- Header -->
<tr>
<td style="background: linear-gradient(135deg, #FF5A5F 0%, #FC642D 100%); padding:35px 40px; text-align:center;">
    <h1 style="color:#ffffff; margin:0; font-size:28px; font-weight:700; letter-spacing:-0.5px;">
        Airbnb Rewards
    </h1>
    <p style="color:rgba(255,255,255,0.9); margin:8px 0 0; font-size:14px;">
        Exclusive Member Invitation
    </p>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:40px;">

    <h2 style="color:#484848; font-size:22px; margin:0 0 15px; font-weight:600;">
        Congratulations! You're Eligible.
    </h2>

    <p style="color:#767676; font-size:15px; line-height:1.6; margin:0 0 20px;">
        Great news! You've been selected to receive a chance to win a
        <strong style="color:#484848;">$750 credit</strong> towards your next Airbnb stay.
        This exclusive offer is available for a limited time.
    </p>

    <!-- Reward Box -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:25px 0;">
    <tr>
    <td style="background-color:#FFF8F6; border:2px solid #FFE0DB; border-radius:10px; padding:25px; text-align:center;">
        <p style="color:#FF5A5F; font-size:42px; font-weight:700; margin:0;">$750</p>
        <p style="color:#767676; font-size:14px; margin:8px 0 0;">Airbnb Travel Credit</p>
    </td>
    </tr>
    </table>

    <p style="color:#767676; font-size:15px; line-height:1.6; margin:0 0 25px;">
        To claim your reward, simply confirm your details below.
        It only takes 30 seconds!
    </p>

    <!-- CTA Button -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
    <td align="center">
        <a href="{offer_link}" target="_blank"
           style="display:inline-block; background:#FF5A5F; color:#ffffff;
                  font-size:16px; font-weight:600; text-decoration:none;
                  padding:15px 45px; border-radius:8px;
                  box-shadow:0 4px 12px rgba(255,90,95,0.35);">
            Claim Your $750 Now &rarr;
        </a>
    </td>
    </tr>
    </table>

    <p style="color:#b0b0b0; font-size:12px; text-align:center; margin:25px 0 0; line-height:1.5;">
        This offer expires soon. Limited availability.
    </p>

</td>
</tr>

<!-- Divider -->
<tr>
<td style="padding:0 40px;">
    <hr style="border:none; border-top:1px solid #ebebeb; margin:0;">
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:25px 40px; text-align:center;">
    <p style="color:#b0b0b0; font-size:11px; margin:0; line-height:1.6;">
        You're receiving this because you expressed interest in travel rewards.<br>
        &copy; 2026 Airbnb Rewards Program. All rights reserved.
    </p>
</td>
</tr>

</table>
<!-- End Main Container -->

</td>
</tr>
</table>

</body>
</html>"""

    return subject, html


def template_airbnb_simple(offer_link, recipient_email=""):
    """Simple text-style template - less likely to trigger spam filters."""

    subject = "Your Airbnb travel reward is waiting"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0; padding:0; background-color:#ffffff; font-family: Arial, sans-serif;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="padding:40px; max-width:600px;">

    <p style="color:#333333; font-size:15px; line-height:1.7; margin:0 0 15px;">
        Hi there,
    </p>

    <p style="color:#333333; font-size:15px; line-height:1.7; margin:0 0 15px;">
        I wanted to let you know that you've been selected for a special opportunity
        to receive a <strong>$750 Airbnb travel credit</strong>.
    </p>

    <p style="color:#333333; font-size:15px; line-height:1.7; margin:0 0 15px;">
        All you need to do is confirm your details here:
    </p>

    <p style="margin:20px 0;">
        <a href="{offer_link}" style="color:#FF5A5F; font-size:15px; font-weight:600;">
            Click here to claim your reward &rarr;
        </a>
    </p>

    <p style="color:#333333; font-size:15px; line-height:1.7; margin:0 0 15px;">
        This is a limited-time offer, so don't wait too long!
    </p>

    <p style="color:#333333; font-size:15px; line-height:1.7; margin:25px 0 0;">
        Best,<br>
        Airbnb Rewards Team
    </p>

</td>
</tr>
</table>

</body>
</html>"""

    return subject, html


def template_airbnb_urgency(offer_link, recipient_email=""):
    """Urgency/scarcity template with countdown feel."""

    subject = "FINAL NOTICE: Your $750 Airbnb credit expires tonight"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#1a1a2e; font-family: Arial, Helvetica, sans-serif;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#1a1a2e; padding:30px 0;">
<tr>
<td align="center">

<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#16213e; border-radius:12px; overflow:hidden; border:1px solid #0f3460;">

<!-- Header -->
<tr>
<td style="background-color:#0f3460; padding:30px 40px; text-align:center;">
    <p style="color:#e94560; font-size:12px; font-weight:700; letter-spacing:2px; margin:0 0 8px; text-transform:uppercase;">
        &#9888; Final Reminder
    </p>
    <h1 style="color:#ffffff; margin:0; font-size:26px; font-weight:700;">
        Your $750 Airbnb Credit
    </h1>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:35px 40px; text-align:center;">

    <p style="color:#a2a2b8; font-size:15px; line-height:1.7; margin:0 0 20px;">
        We've been trying to reach you. Your <strong style="color:#ffffff;">$750 Airbnb
        travel credit</strong> is about to expire and we don't want you to miss out.
    </p>

    <!-- Amount Box -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
    <tr>
    <td style="background-color:#0f3460; border-radius:10px; padding:20px; text-align:center;">
        <p style="color:#e94560; font-size:38px; font-weight:700; margin:0;">$750.00</p>
        <p style="color:#a2a2b8; font-size:13px; margin:6px 0 0;">Available Balance</p>
    </td>
    </tr>
    </table>

    <!-- CTA -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:25px 0;">
    <tr>
    <td align="center">
        <a href="{offer_link}" target="_blank"
           style="display:inline-block; background:linear-gradient(135deg, #e94560, #FF5A5F);
                  color:#ffffff; font-size:16px; font-weight:700; text-decoration:none;
                  padding:15px 50px; border-radius:8px;">
            Claim Before It Expires &rarr;
        </a>
    </td>
    </tr>
    </table>

    <p style="color:#555570; font-size:12px; margin:15px 0 0;">
        Offer expires in less than 24 hours.
    </p>

</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:20px 40px; text-align:center; border-top:1px solid #0f3460;">
    <p style="color:#555570; font-size:11px; margin:0; line-height:1.5;">
        &copy; 2026 Airbnb Rewards. All rights reserved.
    </p>
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>"""

    return subject, html


# ─── Template Registry ────────────────────────────────────────────────────────
TEMPLATES = {
    "1": {"name": "Professional (Airbnb Style)",   "func": template_airbnb_reward},
    "2": {"name": "Simple Text (Less Spam)",       "func": template_airbnb_simple},
    "3": {"name": "Urgency / Dark Theme",          "func": template_airbnb_urgency},
}
