import re

with open('debug.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Look for the pattern we saw earlier
# "title":"..."
matches = re.findall(r'"title":"([^"]+)"', content)
print(f"Found {len(matches)} potential titles.")
if matches:
    print("Samples:", matches[:3])

company_matches = re.findall(r'"postingCompanyName":"([^"]+)"', content)
print(f"Found {len(company_matches)} potential companies.")
if company_matches:
    print("Samples:", company_matches[:3])

# Inspect the surrounding context of a title match to find the parent JSON object
if matches:
    first_match_idx = content.find(matches[0])
    start = max(0, first_match_idx - 100)
    end = min(len(content), first_match_idx + 200)
    print(f"\nContext around first match:\n{content[start:end]}")
