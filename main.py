import argparse
import time
import webbrowser
from datetime import datetime

from agent import search_scholarships, filter_results, summarize_text, save_to_csv, save_to_html

def run():
    print(">> RUN STARTED")
    parser = argparse.ArgumentParser(description="ScholarBot - Smart Scholarship Finder")
    parser.add_argument("--keywords", type=str, help="Keywords to search, comma-separated", required=False)
    parser.add_argument("--country", type=str, help="Target country", default="")
    parser.add_argument("--tuition", type=int, help="Max tuition budget", default=0)
    parser.add_argument("--output", type=str, help="Output filename base (without extension)", default="search_results")
    parser.add_argument("--retries", type=int, help="Number of retries for search if nothing found", default=3)
    args = parser.parse_args()

    if not args.keywords:
        print("Keywords are required. Use --keywords to pass comma-separated values.")
        return

    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    country = args.country.strip().lower()
    max_tuition = str(args.tuition) if args.tuition > 0 else ""

    query = f"{' '.join(keywords)} scholarships in {country}".strip()

    results = []
    filtered = []
    for attempt in range(args.retries):
        print(f"\n[TRY {attempt+1}] Searching DuckDuckGo for: {query}\n")
        results = search_scholarships(query)
        print("[INFO] Total results:", len(results))

        filtered = filter_results(results, keywords, country, max_tuition)
        print("[INFO] After filtering:", len(filtered))

        if filtered:
            break
        else:
            print("[INFO] No results matched your filters. Retrying...\n")
            time.sleep(2)

    if not filtered:
        print("Still no results after all retries. Try different keywords or reduce filtering.")
        return

    final_data = []
    for idx, r in enumerate(filtered):
        title = r.get("title", "")
        url = r.get("href", "")
        body = r.get("body", "")
        print(f"\nResult #{idx+1}: {title}")
        print(f"URL: {url}")
        print("Summary:")
        summary = summarize_text(body)
        print(summary)

        final_data.append({"Title": title, "URL": url, "Summary": summary})
        time.sleep(1)

    save_to_csv(final_data, f"{args.output}.csv")
    save_to_html(final_data, f"{args.output}.html")
    print(f"[INFO] Results saved to {args.output}.csv and {args.output}.html")
    webbrowser.open(f"{args.output}.html")

if __name__ == "__main__":
    run()
