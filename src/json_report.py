import json

def write_json_report(page_data, filename="report.json"):
    # Convert values to a list and sort by URL
    pages = sorted(page_data.values(), key=lambda p: p["url"])
    
    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
    
    print(f"Report successfully written to {filename}")