import sys

def read_fasta(fasta_path):
    with open(fasta_path, 'r') as f:
        return f.read()

def read_fusion_peptides(peptide_path):
    fusion_headers = []
    fusion_seqs = []
    with open(peptide_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            cols = line.strip().split('\t')
            if len(cols) < 6:
                continue  # skip malformed lines
            header = f">{cols[0]}"
            seq = cols[5]
            fusion_headers.append(header)
            fusion_seqs.append(seq)
    return fusion_headers, fusion_seqs

def write_fasta(fasta_path, proteome_fasta, fusion_headers, fusion_seqs):
    with open(fasta_path, 'w') as f:
        # Write the original proteome
        f.write(proteome_fasta.rstrip() + '\n')
        # Write fusion entries
        for header, seq in zip(fusion_headers, fusion_seqs):
            f.write(f"{header}\n{seq}\n")
        # Write decoy (reverse) entries
        for header, seq in zip(fusion_headers, fusion_seqs):
            rev_header = f">rev{header[1:]}"
            rev_seq = seq[::-1]
            f.write(f"{rev_header}\n{rev_seq}\n")

if __name__ == '__main__':
    # Example usage: python prepare_search_database.py human.fasta fusion_peptides.txt
    human_fasta = 'human_proteome.fasta'  # Change as needed
    fusion_peptides = 'target_peptides.txt'  # Change as needed
    output_fasta = 'fusion_db_search_database.fa'

    proteome_fasta = read_fasta(human_fasta)
    fusion_headers, fusion_seqs = read_fusion_peptides(fusion_peptides)
    write_fasta(output_fasta, proteome_fasta, fusion_headers, fusion_seqs)
    print(f"Combined FASTA written to {output_fasta}") 
