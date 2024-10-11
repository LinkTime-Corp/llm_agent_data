import os

import click
import pandas as pd

script_path = os.path.dirname(os.path.abspath(__file__))


def get_final_path(filename: str) -> str:
    final_filepath = filename
    if not os.path.isabs(final_filepath):
        # If it's not an absolute path, get the current working directory
        current_dir = os.getcwd()
        # Join the current working directory with the filename
        final_filepath = os.path.join(current_dir, filename)
        if not os.path.exists(final_filepath):
            final_filepath = os.path.join(script_path, filename)
    return final_filepath


@click.command()
@click.option(
    "-a",
    "--file-a",
    required=True,
    type=click.Path(),
    help="Path to the first CSV file (File A)",
)
@click.option(
    "-b",
    "--file-b",
    required=True,
    type=click.Path(),
    help="Path to the second CSV file (File B)",
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    type=click.Path(),
    help="Path to the output CSV file",
)
def combine_csv(file_a: str, file_b: str, output_file: str):
    # Load both CSV files as dataframes
    df_a = pd.read_csv(get_final_path(file_a))
    df_b = pd.read_csv(get_final_path(file_b))

    # Merge the two dataframes based on the 'name' column.
    # We use an "outer" join to ensure that all rows from both dataframes are included.
    combined_df = pd.merge(df_a, df_b, on="name", how="outer", suffixes=("_A", "_B"))

    # Create a new dataframe where we prioritize values from File A
    final_data = []
    columns = [
        "name",
        "tagline",
        "web_site",
        "main_product_or_service",
        "categories",
        "web_domain",
    ]

    for _, row in combined_df.iterrows():

        if not row["name"]:
            continue

        final_row = {}
        final_row["name"] = row["name"]

        # Iterate over the other columns to prioritize values from File A if available
        for col in columns[1:]:
            col_a = f"{col}_A"
            col_b = f"{col}_B"

            if pd.notna(row[col_a]):
                final_row[col] = row[col_a]
            elif pd.notna(row[col_b]):
                final_row[col] = row[col_b]
            else:
                final_row[col] = None

        final_data.append(final_row)

    # Create the final dataframe
    final_df = pd.DataFrame(final_data, columns=columns)

    # Save the result to a new CSV file
    final_df.to_csv(output_file, index=False)

    print("CSV files have been successfully combined.")


if __name__ == "__main__":
    combine_csv()
