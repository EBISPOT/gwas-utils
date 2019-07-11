#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;
use URI::Encode;
use JSON;
use Getopt::Long qw(GetOptions);

# Initialize URI encoder object:
our $uri = URI::Encode->new( { encode_reserved => 0 } );


my $traitFile= '';
my $ancestryFile = '';
my $geneFile = '';
my $logFile = '';
my $help = 0;
our $outputFolder = 'output';

# Collection of tested classes:
our %Dispatch_table = (
    'variant' => \&is_variant,
    'trait'=> \&is_trait,
    'gene' => \&is_gene,
    'pmid' => \&is_pubmedId,
    'ancestry' => \&is_ancestry,
    'cytoband' => \&is_cytological_band,
    'consortia' => \&is_consortia,
    'region' => \&is_region,
    'study' => \&is_study,
    'author' => \&is_author
);

# Search terms to omit from analysis:
our %omitTerms = ("breast carcinoma" => 1,
    "rs7329174" => 1,
    "yao" => 1,
    "2q37.1" => 1,
    "hbs1l" => 1,
    "6:16000000-25000000" => 1
);

# Parsing command line arguments:
GetOptions ("traitFile|t=s" => \$traitFile,
            "ancestryFile|a=s" => \$ancestryFile,
            "geneFile|g=s" => \$geneFile,
            "logFile|l=s" => \$logFile,
            "outputFolder|o=s" => \$outputFolder,
            "help|h=s" => \$help)
  or display_help();

# Reading phenotype terms:
our $traitDefinitions = read_term_lists($traitFile);
printf STDERR ("[Info] Number of trait related terms: %s\n", scalar keys %{$traitDefinitions});

# # Reading gene terms:
our $geneDefinitions = read_term_lists($geneFile);
printf STDERR ("[Info] Number of gene related terms: %s\n", scalar keys %{$geneDefinitions});

# # Reading ancestry related terms:
our $ancestryDefinitions = read_term_lists($ancestryFile);
printf STDERR ("[Info] Number of ancestry related terms: %s\n", scalar keys %{$ancestryDefinitions});

# Initialize parameters:
my $fileHandles = generate_fileHandles(keys %Dispatch_table);
my %class_overlap = ();
my %classification = ();
my $sum = 0;

if ( not defined $logFile ){
    die "[Error] Logfile needs to be specified. Exiting.\n";
}
elsif ( not -e $logFile ){
    die "[Error] Logfile ($logFile) could not be opened. Exiting.\n";
}

# Open logFile
open my $LOGFILE, "<", $logFile;
while ( my $line = <$LOGFILE> ){
    chomp $line;

    # Pre-process search term:
    my ($count, $term) = split(/\t/,$line);
    my $clean_term = clean_text($term);

    # Excluding omitted terms:
    next if exists $omitTerms{$clean_term};

    # Keeping track of the number of queries:
    $sum += $count;

    # What are the assigned terms:
    my $classes = classify_term($clean_term);

    my $classCount = scalar @{$classes};
    $class_overlap{$classCount} += $count;

    foreach my $class (@{$classes}){
        # Counting queries for each terms:
        $classification{$class} += $count;

        # Saving term for each associated class:
        printf { $fileHandles->{$class} } "%s\t%s\t%s\n", $count, $clean_term, join(", ", @{$classes});
    }

}

print "\n\n[Info] Total number of queries: $sum\n";
print "[Info] Total number of unique search terms: $.\n";

##
## output counts for each class:
##
print "\n\n[Info] The search terms classified as follows:\n";
print "Bin Count Percent\n";
foreach my $class (keys %classification){
    printf "%s %s %.3f%%\n", $class, $classification{$class}, $classification{$class} / $sum * 100
}

##
## Output overlap between the classes:
##
print "\n\n[Info] Overlap across all categories:\n";
print "Bin Count Percent\n";
foreach my $ctOverlap (keys %class_overlap){
    printf "%s %s %.5f%%\n", $ctOverlap, $class_overlap{$ctOverlap}, $class_overlap{$ctOverlap} / $sum * 100
}

##
## Functions
##

# Function to reads a list from a file provided as input and returns a hashref
sub read_term_lists {
    my $fileName = shift;

    # Testing files:
    if ( not defined $fileName ){
        die "[Error] Term list file is not defined. Exiting.";
    }
    elsif ( not -e $fileName ){
        die "[Error] Term list file could not be opened.";
    }

    # Opening file:
    my %hash = ();
    open my $TERMFILE, "<", $fileName;
    while (my $line = <$TERMFILE>){
        chomp $line;
        $line = lc $line;
        $hash{$line} ++;
    }

    return \%hash;
}

# A collection of steps to clean the search term:
sub clean_text {
    my $text = $_[0];

    # Removing spaces wehre it's required:
    my $term = $_[0];

    # Decode uri:
    my $decodedTerm = $uri->decode($term);

    # Remove leading and trailing whitespace:
    $decodedTerm =~ s/^\s*|\s*$//g;

    # Replace + sign with space:
    $decodedTerm =~ s/\+/ /g;

    # Remove a commonly found string:
    $decodedTerm =~ s/\*\&filter=//g;

    # Returned cleaned term:
    return(lc $decodedTerm) 
}

# Test if a term is a variant or not:
sub is_variant{
    my $term = $_[0];
    $term =~ s/\s//g;
    if ($term =~ /rs\d{3,}/i ||
        $term =~ /exm\d+/i ||
        $term =~ /kgp\d+/i ||
        $term =~ /[xy\d]+:\d+[^-]/ ){
        return 1;
    }
}

# Test if a term is a trait or not:
sub is_trait{
    my $term = $_[0];
    if ($term =~ /efo.\d+/i){
        return 1;
    }
    if ( exists $traitDefinitions->{$term} ){
        return 1;
    }
}

# Test if a term is a gene or not:
sub is_gene{
    my $term = $_[0];
    if ( exists $geneDefinitions->{$term} ){
        return 1;
    }
    # Gene card gene identifier:
    elsif ( $term =~ /gc[\dxy]+[a-z][\d]+/){
        return 1;
    }
    # Is Ensembl gene ID provided:
    elsif ( $term =~ /ensg\d+/){
        return 1;
    }
}

# Test if a term is a pubmedID or not:
sub is_pubmedId {
    my $term = $_[0];
    $term =~ s/[\s,]//g;
    if ( $term =~ /[^\d]*[1-3]\d{7}[^\d]*/i && 
         $term !~ /rs\d+|kgp\d+|exm\d+|[xy\d]:\d+/){
        return 1;
    }
}

# Test if a study is directly requested:
sub is_study {
    my $term = $_[0];
    if ( $term =~ /gcst\d+/){
        return 1;
    }
}

# Test if a term is a cytological band:
sub is_cytological_band {
    my $term = $_[0];
    if ( $term =~ /^[\dxy]+[pq][\d]+/ ){
        return 1;
    }
}

# Test if a term is a genomic region
sub is_region {
    my $term = $_[0];
    $term =~ s/\s|,//g;
    if ( $term =~ /[xy\d]+:[1-9]\d+.+-\d+/){
        return 1;
    }
}

# Test if a term is classified as consortia/dataset
sub is_consortia {
    my $term = $_[0];
    if ( ($term =~ /consort/ || $term =~ /biobank/) && length($term) < 50 ){
        return 1;
    }
}

# Test if ancestry related
sub is_ancestry {
    my $term = $_[0];
    if ( exists $ancestryDefinitions->{$term} ){
        return 1;
    }
}

# Test if author is queried:
sub is_author {
    my $term = $_[0];
    if ( $term !~ /vitamin|hepatitis|cystatin|apolipoprotein/ && $term =~ /\w\s+\D{1,2}$/ ){
        return 1;
    }
}

# A function to return the classes a given search term was classified into:
sub classify_term {

    my $term = $_[0];
    my $selected_classes = [];

    # Looping through all classes and check which one is true:
    foreach my $class (keys %Dispatch_table){
        push @{$selected_classes}, $class if $Dispatch_table{$class}->($term);
    }

    # Return the selected classes:
    return ( scalar @{$selected_classes} > 0 ) ? $selected_classes : ["unclassified"];
}

# A standard help message to guide users to troubleshoot.
sub display_help {
    my $error_message = shift;

    ## TODO: improve help message.

    my $standard_message = "

This script was written to parse GWAS Catalog search terms and to classify into major categories: publication title, author, pmid, gene, variant, region, trait etc.

Usage:

$0 --geneFile <gene list file> --traitFile <trait list file> --ancestryFile <ancestry list file>

Output:

Output is a list of files with the classified search terms.
";

    die $error_message . $standard_message;

}

sub generate_fileHandles {
    my @classes = @_;
    push @classes, 'unclassified';
    my %handles = ();

    foreach my $class (@classes){
        my $fullPath = sprintf("%s/%s_type.txt", $outputFolder, $class);
        open my $h, ">", $fullPath;
        $handles{$class} = $h;
    }

    return \%handles;
}



