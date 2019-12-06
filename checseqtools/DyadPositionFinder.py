import logging
import sys

import click
import pandas as pd
import pyBigWig as pbw

POSITIVE_STRAND = 1
NEGATIVE_STRAND = -1


@click.command()
@click.option('--genes', '-g', type=click.Path(exists=True), default='genes.txt',
              help='Genes information.')
@click.option('--signal', '-s', type=click.Path(exists=True), default='signal.bw',
              help='Dryad signal as a bigWig or bigBed file.')
@click.option('--dryad', '-d', type=int, default=2,
              help='Dryad index.')
@click.option('--output', '-o', type=click.Path(), default='genes-out.txt',
              help='Output file.')
def main(genes, signal, dryad, output):
    '''Prepare BED file used for genome coverage on samples.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if dryad != 2:
        print >> sys.stderr, 'dryad parameter must be 2'
        sys.exit(1)
    genes_info = pd.read_csv(genes, header=None, sep='\t', comment='#')
    bw = pbw.open(signal)
    for gene_info in genes_info:
        chromosome = gene_info[1]
        strand = gene_info[4] == NEGATIVE_STRAND
        first_nucleosome = gene_info[7]
        start = first_nucleosome + (141 if strand else -141)
        end = start + 41 if strand else start - 41;
        next_nucleosome = highest_signal(bw, chromosome, start, end)
        gene_info[11] = next_nucleosome[0]
    pd.to_csv(output, header=None, sep='\t', comment='#')


def highest_signal(bw, chromosome, start, end):
    '''Returns coordinate having the highest signal in the bigWig between specified coordinates'''
    intervals = bw.intervals(chromosome, start, end)
    if not intervals:
        return None
    max = intervals[0]
    for interval in intervals:
        if interval[2] > max[2]:
            max = interval
    return max


if __name__ == '__main__':
    main()
