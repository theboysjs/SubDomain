# Define the domains you want to support
DOMAINS = ["lykcloud.com", "example.org", "example.net"]  
# Define the record types you want to support
RECORD_TYPES = ["A", "AAAA", "CNAME", "TXT"]

# Define the features for each record type
RECORD_FEATURES = {
    "SRV": ["priority", "weight", "port", "target" ],
    # Add more record types and their features as needed
}