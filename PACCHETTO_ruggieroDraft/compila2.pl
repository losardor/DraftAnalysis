#!/usr/bin/perl
$gcc = "gcc -O3 -Wall -g -I/sw/include/gtk-1.2 -I/sw/include/glib-1.2 -I/sw/lib/glib/include -I/usr/X11R6/include -g  -L/usr/lib -L/usr/X11R6/lib ";
$nome=$ARGV[0];
if ($nome =~ /(\.c$)/g ) {
    $out = $nome;
    $out =~ s/\.c//g;
}
else 
{
    $out = $nome.".exe";
};
system( $gcc." -o ".$out." ".$nome);







