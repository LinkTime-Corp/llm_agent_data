import os

import matplotlib.pyplot as plt
import pandas as pd

# read the data from the file

script_path = os.path.dirname(os.path.abspath(__file__))

data_file = os.path.join(script_path, "startup_list.csv")

generic_categories = [
    "|",
    "AI",
    "Research",
    "Software",
    "Technology",
    "Data",
    "Development",
    "Artificial Intelligence",
    "Machine Learning",
]

data = pd.read_csv(data_file)

# Create a DataFrame
df = pd.DataFrame(
    data,
    columns=["name", "tagline", "website", "main_product_or_service", "categories"],
)

# Split categories by the pipe symbol, strip, and flatten the list
df["categories"] = df["categories"].str.split(" \| ")

# Flatten the DataFrame so each company-category pair is in its own row
flat_categories = df.explode("categories")
flat_categories = flat_categories[
    ~flat_categories["categories"].isin(generic_categories)
]


# Count the occurrences of each category
category_distribution = flat_categories["categories"].value_counts()

# Filter out categories with fewer than 2 companies
filtered_category_distribution = category_distribution[category_distribution >= 20]

# Save the category distribution to a CSV file
# categories_yyyymmdd.csv
timestamp = pd.Timestamp.now().strftime("%Y%m%d")
filename = f"categories.{timestamp}.csv"
with open(os.path.join(script_path, filename), "w") as f:
    filtered_category_distribution.to_csv(f)

print(filtered_category_distribution)

# Plot the distribution
plt.figure(figsize=(10, 6))
filtered_category_distribution.plot(kind="bar")
plt.title("Distribution of Companies Across Categories (with at least 2 companies)")
plt.xlabel("Categories")
plt.ylabel("Number of Companies")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
