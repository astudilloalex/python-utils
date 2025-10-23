from utils.log_xml_util import LogXmlUtil

# util = LogXmlUtil(r'D:\Users\Alex\Documents\BancoDelAustro\2025-10-13\10.16.0.113\Logs',
#                  ['IdAplicacion', 'IdServicio', 'IdTransaccion'])

# util.extract_dir_to_csv(r'D:\Users\Alex\Documents\BancoDelAustro\2025-10-13\10.16.0.113\extract_logs.csv')

import csv

def remove_duplicates(input_file: str, output_file: str):
    """
    Reads a CSV file and writes only unique rows to a new file.
    Uniqueness is determined by the combination of all columns.
    """

    unique_rows = set()
    output_data = []

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Create a tuple from the key columns
            key = (row['IdAplicacion'], row['IdServicio'], row['IdTransaccion'])
            if key not in unique_rows:
                unique_rows.add(key)
                output_data.append(row)

    # Write only unique rows to output file
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

    print(f"✅ Unique rows written to: {output_file}")

# Example usage
if __name__ == "__main__":
    remove_duplicates(r'D:\Users\Alex\Documents\BancoDelAustro\2025-10-13\10.16.0.113\extract_logs.csv', r'D:\Users\Alex\Documents\BancoDelAustro\2025-10-13\10.16.0.113\extract_unique_logs.csv')
