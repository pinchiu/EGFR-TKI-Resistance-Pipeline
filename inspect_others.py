import pandas as pd

# Load the processed data
df = pd.read_csv("EGFR_Mutations_Cleaned_Processed.csv")

# Filter for "Other EGFR Mutation"
other_mutations = df[df['Mutation_Group'] == "Other EGFR Mutation"]

# Get unique HGVSp_Short values
unique_others = other_mutations['HGVSp_Short'].unique()

print(f"Total 'Other' mutations: {len(other_mutations)}")
print("Unique protein changes in 'Other EGFR Mutation':")
for mutation in unique_others:
    print(f"- {mutation}")
