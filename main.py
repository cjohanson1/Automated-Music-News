import os
import requests
import feedparser
from google import genai

# 1. Fetch RSS feeds from music trades
RSS_FEEDS = [
    "https://www.musicbusinessworldwide.com/feed/",
    "https://www.digitalmusicnews.com/feed/"
]

articles = []
for feed_url in RSS_FEEDS:
    parsed = feedparser.parse(feed_url)
    for entry in parsed.entries[:5]:  # Grab top 5 newest articles per feed
        articles.append(f"Title: {entry.title}\nSummary: {entry.summary}\n")

payload = "\n---\n".join(articles)

# 2. Call Gemini API to extract and format executive digest
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

# Client picks up GEMINI_API_KEY automatically from environment
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT,
)

summary_markdown = response.text

# 3. Post summary to Slack Webhook (or Teams)
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
if slack_webhook_url:
    requests.post(slack_webhook_url, json={"text": summary_markdown})
else:
    print(summary_markdown)
