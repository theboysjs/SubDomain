DOMAINS = ["lykcloud.com", "example.org", "example.net"]  # Replace with your actual domains
RECORD_TYPES = ["A", "AAAA", "CNAME", "TXT"]
RECORD_FEATURES = {
    "SRV": ["priority", "weight", "port", "target" ],
    # Add more record types and their features as needed
}