#!/usr/bin/perl 

#I testi non puliti devono essere messi nella directory START;
$risp=0;
$testiart=0;

PULIZIA:{
print "\nPulire i testi?(y\\n) ---> ";
$risp_pul=<STDIN>;
chomp ($risp_pul);
if (($risp_pul ne "n") && ( $risp_pul ne "y")){
    redo PULIZIA;
}
}
TESTIART:{
    print "\nTesti artificiali?(y\\n) ---> ";
    $risp_art=<STDIN>;
    chomp($risp_art);
    if($risp_art eq "y"){
	print "  Quanti? ---> ";
	$testiart=<STDIN>;
	chomp($testiart);
      DIZIONARI:{
	  print "\nDizionari in DIZIONARI gia' pronti?(y\\n)";
	  $risp_diz=<STDIN>;
	  chomp($risp_diz);
	  if (($risp_pul ne "y") && ( $risp_pul ne "n")){
	      redo DIZIONARI;
	  }
      }
    }
    elsif($risp_art ne "n"){
	redo TESTIART;
    }
}
ANALISI:{
    print "\nEffettuare l'analisi con tmp? (y\\n)";
    $risp_an=<STDIN>;
    chomp($risp_an);
    if($risp_an eq "y"){
	print "  Dimensione dei file ---> ";
	$risp_an_dim = <STDIN>;
	chomp($risp_an_dim);
    }
    else{
	redo ANALISI;
    }
}
DISTANZE:{
    print "\nMatrice delle distanze? (y\\n)";
    $risp_dist=<STDIN>;
    chomp($risp_dist);
    if (($risp_dist ne "y") && ( $risp_dist ne "y")){
	redo PULIZIA;
    }
}

#PULIZIA: 
if($risp_pul eq "y"){
    opendir(DIR,"START") || die "$!";
    @directory = grep(/^\w/i , readdir DIR);
    closedir(DIR);
    foreach $nomefile (@directory){
	open(FILE,"< START/$nomefile") || die "$!"; 
	$nome = "x" . "$nomefile"; 
	while(defined($riga=<FILE>)){
	    chomp($riga);
	    #print"\n$riga";
	    $riga =~ s/\t/\n/g;
	    $riga =~ s/\r/\n/g;
	    $riga =~ s/\n/ /g;
	    $riga =~ s/  / /g;
	    open(MA,">> START/$nome");
	    print MA $riga;
	    close(MA);
	}
    }
    system("mkdir START2");
    system("mv START/x* START2");
    system("mkdir ORIGINALI");
    system("mv START/* ORIGINALI/");
    system("mv START2/* START");
    system("rmdir START2");
}


@directory=();
#TESTIART: 
if($risp_art eq "y"){
    srand();
#ESTRAZIONE DEI DIZIONARI;
    if($risp_diz eq "n"){
	system("./3provafinals_auto 1000000 START");
	system("mkdir DIZIONARI");
	system("mkdir ARTIFICIALI");
	system("mv v*.txt DIZIONARI");
    }
    
#provv. .dat.
#CREAZIONE TESTI ARTIFICIALI;
    opendir(DIR,"DIZIONARI") || die "$!";
    @directory = grep(/^\w/i , readdir DIR);
    closedir(DIR);
    #print "\n\n\n @directory";
    for($testo=0;$testo<$testiart;$testo++){
	$prefisso= "a"."$testo"; 
	$nomefile=();
	foreach $nomefile (@directory){
	    open(TESTO,"<DIZIONARI/$nomefile") || die "$!";
	    $nome = "$prefisso" . "$nomefile";
	    #print "\n $prefisso + $nomefile = $nome";
	    open(PULITO,">ARTIFICIALI/$nome");
	    $posizione = 0;
	    $posto = 0;
	    $i = 0;
	    @array=();
	    @barray=();
	    while (defined ($riga=<TESTO>)) {
		chomp($riga);   
		$array[$posizione] = $riga;
		$posizione++;  
	    }
	    $righe = scalar(@array);
	    #print "ho letto $righe righe\n";
	    while ($i < 5500){                 #numero parole.
		$a = rand(scalar(@array));
		$b = int($a);
		$barray[$posto] = $array[$b];
		#print "$b \n";
		$posto++;
		$i++;
	    }
	    $output = join('',@barray);
	    print PULITO $output;
	    $lunghezza = length($output);
	    print "$nome e' lungo $lunghezza caratteri\n";
	    close(PULITO);
	    close(TESTO);
	    
	}
    }
    system("mkdir PULITI");
    system("mv START/* PULITI");
    system("mv ARTIFICIALI/* START");
}

#CONFRONTO:
if($risp_an eq "y"){
 echo "sono qui";
system("nice ./bcl1pezza $risp_an_dim $risp_an_dim START START");
}

#DISTANZE:
if($risp_dist eq "y"){
    system("cp tridistanze_auto.pl START/ris_bcl\+$risp_an_dim\-$risp_an_dim");
    system("chmod +x START/ris_bcl\+$risp_an_dim\-$risp_an_dim/tridistanze_auto.pl");
    system("START/ris_bcl\+$risp_an_dim\-$risp_an_dim/tridistanze_auto.pl START/ris_bcl\+$risp_an_dim\-$risp_an_dim/ $risp_art");
#system("cp START/ris_bcl\+$risp_an_dim\-$risp_an_dim/dist.dat ../../");
}
