import json
from pathlib import Path

from models import PropertyData, ReturnData

# Load json file
with Path("real_estates.json").open() as file:
    raw = json.load(file)

# Parse json
data: list[PropertyData] = []
for item in raw:
    try:
        new = PropertyData.model_validate(item["data"]["propertyData"])
    except Exception as e:
        print(f"Error parsing item: {e}")
    else:
        data.append(new)

# Process data
return_data: list[ReturnData] = [
    ReturnData.from_property_data(item)
    for item in data
    if item.presentation_type == "ACTIVE"
]

# Save data
with Path("parsed.json").open("w") as file:
    json.dump([item.model_dump() for item in return_data], file, indent=2)
