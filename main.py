import os
import smtplib
import feedparser
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai

# 1. Fetch RSS Feeds
RSS_FEEDS = [
    "https://www.musicbusinessworldwide.com/feed/",
    "https://www.digitalmusicnews.com/feed/"
]

articles = []
for feed_url in RSS_FEEDS:
    parsed = feedparser.parse(feed_url)
    for entry in parsed.entries[:5]:
        articles.append(f"Title: {entry.title}\nSummary: {entry.summary}\n")

payload = "\n---\n".join(articles)

# 2. Generate Summary via Gemini
PROMPT = f"""
You are an executive music industry analyst. Review the provided article titles and snippets.

Tasks:
1. Filter out gossip, album reviews, and opinion pieces unless they involve major commercial milestones.
2. Group remaining news into 3 categories:
   - 📈 Business & Deals (M&A, catalog sales, streaming stats, legal/copyright)
   - 🤖 Tech & AI (New tools, platform updates, licensing deals)
   - 🎤 Tours & Live Sector (Major festival news, ticketing updates, arena developments)
3. Provide a 2-sentence summary for each key story, followed by a bulleted key takeaway.
4. Keep the output under 400 words total in Markdown.

Articles to analyze:
{payload}
"""

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT,
)

summary_md = response.text

# 3. Convert Markdown to styled HTML
html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    {markdown.markdown(summary_md)}
  </body>
</html>
"""

# 4. Send via SMTP
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")  # App Password for Gmail
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

if SENDER_EMAIL and SENDER_PASSWORD and RECIPIENT_EMAIL:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📈 Daily Music Industry Executive Digest"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    # Attach both plain text and HTML versions
    msg.attach(MIMEText(summary_md, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Connecting to Gmail SMTP server (Port 587 for TLS)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email sent successfully!")
else:
    print(summary_md)
