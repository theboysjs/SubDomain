DOMAINS = ["lykcloud.com", "example.org", "example.net"]  # Replace with your actual domains
RECORD_TYPES = ["A", "AAAA", "CNAME", "TXT", "MX"]
RECORD_FEATURES = {
    "MX": ["priority"],
    "SRV": ["priority", "weight", "port"],
    # Add more record types and their features as needed
}