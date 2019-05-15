#!/usr/bin/perl
undef $/;
open( FILE,"<$ARGV[0] ");
$file = <FILE>;
close(FILE);

$file =~ s/\n/ - /g;
$file =~ s/ \- \*/\n\*/g;
$file =~ s/\* \- /\*\n/g;
#$file =~ s/\**//g;
$file =~ s/\*+\n//g;

open( FU, ">".$ARGV[0].".pul");
print FU $file;
close(FU);

