# agent.py
import os
os.environ["HF_HOME"] = "N:/HF_CACHE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_TOKEN"] = ""  # force ignore any token errors

from ddgs import DDGS
from transformers import pipeline
from config import SUMMARY_MODEL, MAX_SUMMARY_LEN, DEFAULT_RESULTS
from utils import clean_text, try_parse_number
import pandas as pd
import time

summarizer = pipeline("summarization", model=SUMMARY_MODEL)

def search_scholarships(query, max_results=DEFAULT_RESULTS):
    print(f"\nSearching DuckDuckGo for: {query}\n")
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return list(results)

def summarize_text(text, max_len=100):
    if len(text) < 100:
        return text

    try:
        short_text = text[:1000]
        max_len = min(max_len, len(short_text) // 2)
        summary = summarizer(short_text, max_length=max_len, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return text[:200] + "..."  # just truncate


def filter_results(results, keywords, country, max_budget):
    filtered = []

    # Fuzzy aliases for countries
    COUNTRY_ALIASES = {
        "germany": ["germany", "german", "berlin", "daad", "heidelberg", "tu munich", "rwth", "fraunhofer"],
        "usa": ["usa", "united states", "america", "us"],
        "canada": ["canada", "ontario", "toronto", "canadian", "ubc", "mcgill"],
        "uk": ["uk", "united kingdom", "england", "scotland", "british", "oxford", "cambridge"]
    }

    country_terms = COUNTRY_ALIASES.get(country.lower(), [country.lower()])

    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        full_text = (title + " " + body).lower()

        # Check for at least one keyword match
        if keywords and not any(k.lower() in full_text for k in keywords if k.strip()):
            continue

        # Check for country relevance
        if country and not any(term in full_text for term in country_terms):
            continue

        # Tuition filtering with fallback for "fully funded"
        if max_budget:
            try:
                numbers = [int(s.replace(",", "")) for s in full_text.split() if s.replace(",", "").isdigit()]
                if numbers:
                    if all(n > int(max_budget) for n in numbers):
                        continue
                else:
                    if "fully funded" not in full_text:
                        continue
            except:
                pass  # Fail silently on parsing

        # If passed all filters, include it
        filtered.append(r)

    print(f"[INFO] Total results: {len(results)}")
    print(f"[INFO] After filtering: {len(filtered)}")
    return filtered

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"[INFO] Results saved to {filename}")

def save_to_html(data, filename="results.html"):
    html = "<html><head><title>ScholarBot Results</title></head><body>"
    html += "<h2>ScholarBot Search Results</h2><ul>"
    for i, item in enumerate(data, 1):
        html += f"<li><strong>{i}. <a href='{item['URL']}'>{item['Title']}</a></strong><br>"
        html += f"{item['Summary']}</li><br><br>"
    html += "</ul></body></html>"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
