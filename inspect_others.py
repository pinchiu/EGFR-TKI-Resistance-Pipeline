import pandas as pd

# Load the processed data
df = pd.read_csv("EGFR_Mutations_Cleaned_Processed.csv")

# Filter for "Other EGFR Mutation"
other_mutations = df[df['Mutation_Group'] == "Other EGFR Mutation"]

# Get unique HGVSp_Short values
unique_others = other_mutations['HGVSp_Short'].unique()

# Save to CSV
other_counts = other_mutations['HGVSp_Short'].value_counts()
output_path = "results/other_mutations_list.csv"
other_counts.to_csv(output_path, header=["Count"])

print(f"Total 'Other' mutations: {len(other_mutations)}")
print(f"Detailed list saved to: {output_path}")
print("\nTop 10 'Other' mutations:")
print(other_counts.head(10))
