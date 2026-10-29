from flask import current_app
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = (
    "You are an assistant inside a small-business CRM. "
    "Write only from the data provided. Never invent facts, prices, dates, "
    "or promises that are not in the data. If something is missing, leave it out. "
    "Use a professional, warm, concise tone. Output plain text only, no markdown."
)


def build_customer_context(customer):
    """Turn a customer's real database records into a text block for the prompt.
    Email and phone are deliberately NOT included."""
    lines = [
        f"Customer name: {customer.full_name}",
        f"Company: {customer.company_name or 'Not provided'}",
        f"Customer type: {customer.customer_type or 'Not provided'}",
        f"Status: {customer.status}",
    ]
    if customer.notes:
        lines.append(f"Notes: {customer.notes}")

    leads = sorted(customer.leads, key=lambda l: l.created_at, reverse=True)[:5]
    if leads:
        lines.append("Leads:")
        for l in leads:
            lines.append(f"- {l.lead_name} (source: {l.lead_source or 'unknown'}, status: {l.status})")

    followups = sorted(customer.followups, key=lambda f: f.followup_date, reverse=True)[:5]
    if followups:
        lines.append("Follow-ups:")
        for f in followups:
            lines.append(f"- {f.followup_date}: {f.purpose or 'Follow-up'} ({f.status})")

    deals = sorted(customer.deals, key=lambda d: d.deal_date, reverse=True)[:5]
    if deals:
        lines.append("Deals:")
        for d in deals:
            lines.append(f"- {d.deal_name}: Rs {float(d.deal_amount):,.2f} ({d.status}, {d.deal_date})")

    activities = sorted(customer.activities, key=lambda a: a.created_at, reverse=True)[:10]
    if activities:
        lines.append("Recent activity:")
        for a in activities:
            lines.append(f"- {a.created_at.strftime('%d %b %Y')}: {a.description}")

    return "\n".join(lines)


def _generate(prompt):
    """Call Gemini. Returns (text, error). Never raises."""
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return None, "AI isn't set up yet. Add GEMINI_API_KEY to your .env file."

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=current_app.config["GEMINI_MODEL"],
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            return None, "The AI returned an empty response. Please try again."
        return text, None
    except Exception as e:
        # Full details go to the terminal only, never to the user.
        current_app.logger.error("Gemini request failed: %s", e)
        return None, "The AI service is unavailable right now. Please try again in a moment."


def draft_followup_email(customer):
    context = build_customer_context(customer)
    prompt = (
        "Write a short follow-up email (under 120 words) to this customer.\n"
        "Start with a subject line. Refer to their latest lead, deal, or follow-up "
        "where relevant. End with a clear next step. Sign off as [Your name].\n\n"
        f"CUSTOMER DATA:\n{context}"
    )
    return _generate(prompt)


def summarize_customer(customer):
    context = build_customer_context(customer)
    prompt = (
        "Summarize this customer's relationship with us in 4 to 5 short bullet "
        "points, each starting with '- '. Finish with one line starting with "
        "'Suggested next step:'.\n\n"
        f"CUSTOMER DATA:\n{context}"
    )
    return _generate(prompt)