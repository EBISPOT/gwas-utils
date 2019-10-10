#!/usr/bin/env perl

# 
use warnings;
use strict;
use JSON;
use Data::Dumper;

# Test if file is given
my $jsonFile = $ARGV[0];
if ( ! defined $jsonFile ){
    die "[Error] input json file is required! Exiting";
}
elsif ( not -e $jsonFile ){
    die "[Error] input json file is could not be opened! Exiting";
}

# Reading trait json:
my $json = read_json($jsonFile);
my $data = decode_json($json);

# Build hash, with unique trait terms:
my %hash = ();
foreach my $trait (@{$data}){
    # Extract all values from synonyms:
    if (exists $trait->{'synonyms'}){ foreach my $synonym (@{$trait->{'synonyms'}}){ $hash{$synonym} = 1 }}

    # Extract all values from reportedTrait:
    if (exists $trait->{'reportedTrait'}){ foreach my $reportedTrait (@{$trait->{'reportedTrait'}}){ $hash{$reportedTrait} = 1 };}

    # Extract all values from mappedTrait:
    if (exists $trait->{'mappedTrait'}){ $hash{$trait->{'mappedTrait'}} = 1;}

    # Extract all values from parent:
    if (exists $trait->{'parent'}){ foreach my $parent (@{$trait->{'parent'}}){ $hash{$parent} = 1 };}

}

# Write out all unique trait terms:
foreach my $trait (keys %hash){
    next if $trait =~ /^\s+$/;
    print "$trait\n";
}

sub read_json {
    my $json_file = $_[0];
    my $traitFile = 'traits.json';
    local $/; #Enable 'slurp' mode
    open my $fh, "<", $traitFile;
    my $json = <$fh>;
    close $fh;
    return $json;
}