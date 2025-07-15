# scholar_search.py

from ddgs import DDGS

from transformers import pipeline
import pandas as pd
import time

# Load summarizer model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def search_scholarships(query, max_results=10):
    print(f"\nSearching DuckDuckGo for: {query}\n")
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return list(results)

def summarize_text(text, max_len=100):
    if len(text) < 100:
        return text
    summary = summarizer(text, max_length=max_len, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def filter_results(results, keywords, country, max_budget):
    filtered = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        full_text = (title + " " + body).lower()

        # Keyword filter
        if any(k not in full_text for k in keywords if k.strip()):
            continue

        # Country filter
        if country and country not in full_text:
            continue

        # Budget filter (if possible)
        if max_budget:
            try:
                numbers = [int(s.replace(",", "")) for s in full_text.split() if s.replace(",", "").isdigit()]
                if all(n > int(max_budget) for n in numbers):
                    continue
            except:
                pass  # skip this if parsing fails

        filtered.append(r)
    return filtered

def run_agent():
    print("🎓 What kind of scholarships are you looking for?")
    query = input("🔍 Search Query: ")

    keywords_input = input("📝 Enter keywords (comma-separated): ")
    keywords = [k.strip().lower() for k in keywords_input.split(",")]

    country = input("🌍 Enter country (or leave blank): ").strip().lower()
    max_budget = input("💸 Max tuition amount (numbers only, or leave blank): ").strip()

    results = search_scholarships(query)

    filtered = filter_results(results, keywords, country, max_budget)
    if not filtered:
        print("\n⚠️ No results matched your filters. Try changing them.\n")
        return

    data = []
    for idx, result in enumerate(filtered):
        title = result.get("title", "")
        href = result.get("href", "")
        body = result.get("body", "")

        print(f"\nResult #{idx+1}: {title}")
        print(f"URL: {href}")
        print("Summary:")
        summary = summarize_text(body)
        print(summary)

        data.append({"Title": title, "URL": href, "Summary": summary})
        time.sleep(1)

    df = pd.DataFrame(data)
    df.to_csv("search_results.csv", index=False)
    print("\n✅ Results saved to search_results.csv\n")

if __name__ == "__main__":
    run_agent()
