import fitz  # PyMuPDF

# Open the PDF file
pdf_path = "pdf/Just-One-Line-not-tagged.pdf"
doc = fitz.open(pdf_path)

# Print out all xref data
xref_len = doc.xref_length()
print(f"Document has {xref_len} xrefs")

for xref in range(1, xref_len):  # Skip item 0 as it's usually the null object
    print(f"\nObject {xref} (stream: {doc.xref_is_stream(xref)})")
    print(doc.xref_object(xref, compressed=False))

# Close the document
doc.close()
# Open the PDF file
# pdf_path = "pdf/Just-One-Line-2-tagged.pdf"
# doc = fitz.open(pdf_path)

# # Print out all xref data
# xref_len = doc.xref_length()
# print(f"Document has {xref_len} xrefs")

# for xref in range(1, xref_len):  # Skip item 0 as it's usually the null object
#     print(f"\nObject {xref} (stream: {doc.xref_is_stream(xref)})")
#     print(doc.xref_object(xref, compressed=False))

# # Close the document
# doc.close()

