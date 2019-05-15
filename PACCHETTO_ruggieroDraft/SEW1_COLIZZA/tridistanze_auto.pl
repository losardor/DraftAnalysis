#!/usr/bin/perl 
use Cwd;
$dir_corrente= cwd . "/$ARGV[0]";
print "\ndir_corrente = $dir_corrente";
opendir (DIR,"$dir_corrente") || die "$!";
@files = grep(/^Contig/i , readdir DIR);
closedir(DIR);
%opere = ();
$numfiles = scalar(@files);
print "\n numfiles: $numfiles \n";
$i = 0;

#crea l'hash con chiave nome testo e values nomi contig.
while ($i < $numfiles) {
  chomp $files[$i];
  if ($ARGV[1] eq "y") {
    ($inutile,$testok)=split('a\d', $files[$i],2);
  } else {
    ($inutile,$testok)=split('Contig.', $files[$i],2);
  }
  push @{$opere{$testok}} , $files[$i];
  $i++;
}

@nomiop = keys %opere;
$nuovifile = scalar(@nomiop);
#unisce le contig della stessa opera in un unico file.
foreach $k (@nomiop) {
  $testov = scalar(@{$opere{$k}});
  $i = 0; 
  while ($i < $testov) {
    open(FINALE,">>$dir_corrente/$k");
	  open(CONTIG,"$dir_corrente/$opere{$k}[$i]");
	  while (defined($riga=<CONTIG>)) {
      chomp $riga;
      ($nome,$numero) = split(' ', $riga);
      $eli = index($numero,"999999"); #viene eliminato.
      if ($eli == -1) {
        print FINALE "$riga \n";
      }
      ;
	  }
    ;
	  close(FINALE);
	  close(CONTIG);
	  $i++;
	  
  }
  ;
}



#ora esistono i file singoli; si lavorera' su quelli uno alla volta.

$m = 0;
$ciclomedia = 0;
@nomiopord = sort(@nomiop);
foreach $k (@nomiopord) {
  open(FINALE,"<$dir_corrente/$k");
  $nome = "M" . "$k";
  $volte=0;

  %hash = ();                   #inizializzazioni
  @medie = ();
  @medmat = ();
    
  #legge il file delle Contig e crea un hash di array. La chiave di ogni array e' il 
  #nome dell'opera e nel corrispondente array ci sono tutte le contig lette. 
    
  while (defined ($riga=<FINALE>)) {
    $volte++;
    chomp $riga;   
    ($chiave,$numero) = split(' ', $riga);
    if ($ARGV[1] eq "y") {
	    ($inutile,$chiavepul)=split('a\d', $chiave,2);
    } else {
	    $chiavepul=$chiave;
    } 
    push @{$hash{$chiavepul}} , $numero;
  }
  ;
  close(FINALE);
    
  @nomi = keys %hash;   #ogni elemento del vettore e' un nome di opera
  $numeronome = 0;
    
  foreach $k (@nomi) {
    $i = 0 ;
    $somma = 0;
    $media = 0;
    $elementi = scalar(@{$hash{$k}});
    #print "scalar(@{$hash{$nome}}) " ;
    #print "$elementi";
    while ($i<$elementi) {
	    $somma = $somma + $hash{$k}[$i];
	    $i++;
    }
    ;
    $media = $somma / $i;
    #print "media:   $media  \n\n";
    $medie[$numeronome] = sprintf("%6f --- $k \n",$media);
    $medmat[$numeronome] = sprintf("$k --- %6f \n",$media);
    $numeronome++;
  }
  ;
  $medieout = join("" ,sort @medie);
  open(PULITO,">$dir_corrente/$nome");
  printf PULITO ("%10s", $medieout);
  close(PULITO);

  $k = 0;
  $i = 0;
  @alfa = sort(@medmat);
    
  #print "@alfa \n\n\n";
  foreach $k (@alfa) {
    chomp $k;
    ($inutile,$numero) = split(' --- ',$k,2);
    $rigamat[$i] = $numero;
    $posizioni[$i] = $inutile;
    $i++; 
  }
  ; 
  #if ($m != 0) {
  push @{ $AoA[$m] }, @rigamat;
  #print scalar( @{ $AoA[$m] });
  #print "@rigamat = rigamat  \n\n";
  $m++;
   
}
;

#stampa la matrice delle entropie.In @posizioni ci sono i nomi delle righe(colonne).
open(MAT,">$dir_corrente/mat.txt");
for $k ( @AoA ) {
  print MAT "@$k \n";
}
print MAT "@posizioni \n"; 
close (MAT);
#print "@posizioni \n"; 
#print "matrice =  $AoA[0][0] \n\n\n";

#Resta da fare la matrice delle distanze.
#print "fino a qui";
$i = 0;
$j= 0;
#while($AoA[$i][$j])
$dim = $#AoA;
print "\t dim = $dim+1 \n";
for ($i=0;$i<=$dim;$i++) {
  for ($j=0;$j<=$dim;$j++) {
    $numero =($AoA[$i][$j])/($AoA[$j][$j]) + ($AoA[$j][$i])/($AoA[$i][$i]) - 2;
    @rigamat[$j] = sprintf("%6f",$numero);
    #print "numero = $numero \n";
  }
  push @{ $matdist[$i] }, @rigamat;
}
;
$conta_no = 0;
for ( $i = 0; $i<$dim; $i++) {
  for ( $j = ($i+1); $j <$dim; $j++) {
    $c = 0 ;
    for ( $k = 0; $k<$dim; $k++) {
	    if (   $matdist[$i][$j] > ( $matdist[$i][$k] + $matdist[$k][$j] ) ) {
        $matdist[$i][$j] = ( $matdist[$i][$k] + $matdist[$k][$j] );
        $c++;
	    }
      ;
    }
    ;
    $matdist[$j][$i] = $matdist[$i][$j];
    if ( $c > 0 ) {
	    $conta_no++;
    }
    ;
  }
  ;
}
;
printf("Distanze non triangolari: %3d \n",$conta_no); 

open (DIST,">$dir_corrente/dist.dat");
print "sono qui\n";
$i=0;
print "sono qui\n";
$dimv = $dim + 1;
print DIST "$dimv \n";
for $k (@matdist) {
  print DIST"$posizioni[$i]  @$k \n";
  $i++;
}
print DIST "@posizioni \n";
close (DIST); 
%die;

