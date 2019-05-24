import logging
import os
import subprocess

import click

BASE_SCALE = 1000000


@click.command()
@click.option('--samples', '-s', type=click.File('r'), default='samples.txt',
              help='Sample names listed one sample name by line.'
              ' The first line is ignored.')
@click.option('--threads', '-t', default=1,
              help='Number of threads used to process data.')
def main(samples, threads):
    '''Analyse Martin et al. data from November 2018 in Genetics.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    next(samples)
    samples_lines = samples.read().splitlines()
    for sample_line in samples_lines:
        if sample_line.startswith('#'):
            continue
        sample_info = sample_line.split('\t');
        sample = sample_info[0]
        bam_to_bed(sample, threads)


def bam_to_bed(sample, threads):
    print ('Convert BAM to BED for sample {}'.format(sample))
    bam = sample + '.bam'
    bedpe = sample + '.bedpe'
    bam_to_bedpe(bam, bedpe, threads)
    bed_raw = sample + "-raw.bed"
    bedpe_to_bed(bedpe, bed_raw)


def bam_to_bedpe(bam, bedpe, threads=None):
    '''Convert BAM file to BEDPE.'''
    sort_output = bam + '.sort'
    cmd = ['samtools', 'sort', '-n']
    if not threads is None:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', sort_output, bam])
    logging.debug('Running {}'.format(cmd))
    subprocess.call(cmd)
    if not os.path.isfile(sort_output):
        raise AssertionError('Error when sorting BAM ' + bam)
    cmd = ['bedtools', 'bamtobed', '-bedpe', '-mate1', '-i', sort_output]
    logging.debug('Running {}'.format(cmd))
    with open(bedpe, "w") as outfile:
        subprocess.call(cmd, stdout=outfile)
    if not os.path.isfile(bedpe):
        raise AssertionError('Error when converting BAM ' + sort_output + ' to BEDPE')
    os.remove(sort_output)


def bedpe_to_bed(bedpe, bed):
    '''Converts BEDPE file to BED by merging the paired reads.'''
    merge_output = bedpe + '-merge.bed'
    with open(bedpe, "r") as infile:
        with open(merge_output, "w") as outfile:
            for line in infile:
                if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                    outfile.write(line)
                    continue
                columns = line.rstrip('\r\n').split('\t')
                start1 = int(columns[1])
                end1 = int(columns[2])
                start2 = int(columns[4])
                end2 = int(columns[5])
                start = min(start1, start2)
                end = max(end1, end2)
                outfile.write(columns[0])
                outfile.write("\t")
                outfile.write(str(start))
                outfile.write("\t")
                outfile.write(str(end))
                for i in range(6, len(columns)):
                    outfile.write("\t")
                    outfile.write(columns[i])
                outfile.write("\n")
    cmd = ['bedtools', 'sort', '-i', merge_output]
    logging.debug('Running {}'.format(cmd))
    with open(bed, "w") as outfile:
        subprocess.call(cmd, stdout=outfile)
    if not os.path.isfile(bed):
        raise AssertionError('Error when sorting BED ' + merge_output + ' to ' + bed)
    os.remove(merge_output)


if __name__ == '__main__':
    main()
