/* versione di lz77 che stampa il dizionario estratto da un testo */
#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <math.h>
#include <unistd.h>
#include <fcntl.h>

#define  LUNGNOME 80
#define  LUNGPATHNOME 160
#define  MAX_WIN 70000

int PICCOLO;
int GRANDE;
int DIMENSIONE;
char *RIS;

int window;

struct info_file{
  unsigned int lung;
  char *buff;
  char *path_nome[LUNGPATHNOME];
  char *nome[LUNGNOME];
  unsigned  int *indice;
  unsigned  int ultimo[256];
};

struct info_file *G;
int Ng;
int *lun_zip;


int calcola(void){
  int p,pmax,m_lung,q,qmax,q_lung,lung;
  int k,fraz,trovata;
  int i,h,len;
  int finestra;
  char parola[500], *lettera, nomevoc[30];
  FILE *foo;

  strcpy(parola,"");
  finestra = 0;
  h = 0;
  while( h < Ng ) {
    strcpy(nomevoc,"");
    strcat(nomevoc,"v");
    strcat(nomevoc,G[h].nome); 
    foo=fopen(nomevoc,"w");
    fclose (foo);
    window = 32768;
    i = 1; /*window*/
    /*lettera = G[h].buff;*/
    ff("\n G[h].lung = %d \n", G[h].lung);
    while(i < /*DIMENSIONE*/G[h].lung) {
      
      lettera = G[h].buff;
      m_lung = 1;
      q_lung = 1;
      /*p = G[h].ultimo[(unsigned char) G[h].buff[i]];*/
      p = G[h].indice[i];
      /*q = G[h].ultimo[(unsigned char) G[h].buff[i+1]];*/
      q = G[h].indice[i+1];
      /*printf(" ciclo: %d ; p = %d ; q = %d \n",i,p,q);*/
      pmax = 0;
      qmax = 0;
      finestra = i - window;
      while( (p != 0) && (p > finestra) ) {
        lung = 1;
        while( (G[h].buff[i+lung] == G[h].buff[p+lung]) && (p+lung <= G[h].lung)/*&& (i+lung <= l)*/ && (i != p+lung)) {
          lung++;
          /*printf("\t\t %d\n",lung);*/
        };
        if( lung > m_lung ) {
          m_lung = lung;
          pmax = p;
        };
        if( lung > 2 ) {
          lung = 1;
          while( q > pmax + 1) {
            lung = 1;
            while( (G[h].buff[i+1+lung] == G[h].buff[q+lung])  
                   && (q+lung <= G[h].lung)
                   /*&& (i+1+lung <= l )*/
                   && (i+1 != q+lung) ) {
              lung++;
            };
            if( lung > q_lung ) {
              q_lung = lung;
              qmax = q;
            };
            q = G[h].indice[q];
          };
        };
        p = G[h].indice[p];
      };
      /* ricerca residua su q */
      if( m_lung > 1 ) {
        lung = 1;
        while( (q != 0) && (q > finestra) ) {
          lung = 1;
          while( (G[h].buff[i+1+lung] == G[h].buff[q+lung]) 
                 && (q+lung <= G[h].lung)
                 /*&& (i+1+lung <= l )*/ 
                 && (i+1 != q+lung))  {
            lung++;
          };
          if( lung > q_lung ) {
            q_lung = lung;
            qmax = q;
          };
          q = G[h].indice[q];
        };
      };
      if( q_lung < m_lung +1 ) { 
        if( m_lung > 2 ) {
          if(m_lung < 300){
            strncat(parola,lettera+i,m_lung);
          }
          else{
            k=0;
            fraz=m_lung;
            while(fraz>0){
              trovata = MIN(fraz,300);
              strncat(parola,lettera+i+k,trovata);
              foo = fopen(nomevoc,"a");
              fprintf(foo,"%s",parola);
              fclose (foo);
              strcpy(parola,"");
              fraz = fraz - 300;
              k = k + 300;
              //printf("k=%d \n", k);
            }
          }
          strcat(parola,"\n");
          i += m_lung;
        }
        else {
          i++;
        };
      }
      else {
        if(q_lung > 2){ 
          if (q_lung<300){
            strncat(parola,lettera+i+1,q_lung);
          }
          else{
            k=0;
            fraz=q_lung;
            while(fraz>0){
              trovata = MIN(fraz,300);
              strncat(parola,lettera+i+1+k,trovata);
              foo = fopen(nomevoc,"a");
              fprintf(foo,"%s",parola);
              fclose (foo);
              strcpy(parola,"");
              fraz = fraz - 300;
              k = k + 300;
              // printf("k=%d \n", k);
            }
          }
          strcat(parola,"\n");
          i += q_lung+1;
        } 
        else {
          i++;
        };
      };
      len = strlen(parola);
      /*printf("\t\t\t\t %d \n",len);*/
      if(len > 150){
        foo = fopen(nomevoc,"a");
        fprintf(foo,"%s",parola);
        fclose (foo);
        strcpy(parola,"");
        /*printf("nome file trattato %s ",G[h].nome);*/
      };
    };
    
    
    /*printf("parola che sara' stampata : %s \n", parola);*/
    foo = fopen(nomevoc,"a");
    /*printf("prova ");*/
    fprintf(foo,"%s",parola);
    fclose (foo);
    strcpy(parola,"");
    printf("\n     FINE.");
    h++;
  };
  return 1;
}


int carica_file_g(char *nome_dir_g) {
  struct dirent **namelist;
  struct stat stbuf;
  char *tmp_nome;
  int n,i,j,k,ifp,err;


  /* legge la directory di nome nome_dir_g;
     alloca un numero sufficiente di strutture info_file,
     seleziona i file regolari e ne memorizza nome, path+nome
     lunghezza */

  tmp_nome = (char *)  malloc(sizeof(char[LUNGPATHNOME]));
  n = scandir(nome_dir_g, &namelist, 0, alphasort);
  i = 0;
  Ng = 0;

  if(n == -1 ) {
    printf("ERRORE in lettura della directory %s\n",nome_dir_g);
    exit(1);
  };

  /* n e' il numero di file nella directory, 
     Ng e' variabile globale che contiene il numero di testi= file regolari
     che non siano NASCOSTI (non cominciano con .)
  */

  G = (struct info_file *) calloc(n,sizeof(struct info_file));


  while( i <= n-1 ) {
    strcpy(tmp_nome,nome_dir_g);
    strcat(tmp_nome,namelist[i]->d_name);
    stat(tmp_nome,&stbuf);
    err = 0;
    if( S_ISREG(stbuf.st_mode) == 1 && memcmp(namelist[i]->d_name,".",1) != 0)
      {
        G[Ng].lung = (unsigned int) /*DIMENSIONE;*/MIN(DIMENSIONE,(int) stbuf.st_size);
       
        strcpy(G[Ng].path_nome,tmp_nome);
        strcpy(G[Ng].nome,namelist[i]->d_name);
        /* alloco la parte della struttura necessaria. 
           pieno di WARNING non capisco qual e' il modo corretto */
        G[Ng].indice = (unsigned int *) 
          calloc((int) DIMENSIONE+1,sizeof(unsigned int));
        G[Ng].buff = (char *) 
          calloc((int) DIMENSIONE+1,sizeof(char));
        if( G[Ng].indice == NULL || G[Ng].buff == NULL) {
          err = 1;
        };
        /* carica il file e ne costruisce la copia a forma di indici e 
           gli indici delle ultime occorrenze dei caratteri. */
        ifp = open(tmp_nome, O_RDONLY);
        if( ifp == -1 ) {
          err = 2;
        };
        k =  read(ifp,G[Ng].buff+1,(int) DIMENSIONE);
        if( k == 0 ) {
          err = 3;
        }
        else {
          if( k != G[Ng].lung ) {
            printf("Attenzione: file %s byte letti %d su %d \n",
                   namelist[i]->d_name,k,G[Ng].lung);
            G[Ng].lung = k;
          };
          for(j=0;j<256; j++) {
            G[Ng].ultimo[j] = 0;
          };
          for(j=1;j<= DIMENSIONE; j++) {
            G[Ng].indice[j] = G[Ng].ultimo[(unsigned char) G[Ng].buff[j]];
            G[Ng].ultimo[(unsigned char) G[Ng].buff[j]] = j;
            /*printf(" j = %6d, indice = %6d, ultimo = %6d \n",j, G[Ng].indice[j], G[Ng].ultimo[(unsigned char) G[Ng].buff[j]]);*/ 
          };

          printf("\n G[Ng].lung = %d \t Ng= %d\n\n " , G[Ng].lung, Ng); 
        };
        if( err > 0 ) {
          /* errore 1 (grave) non alloca 
             errore 2 (strano) non apre il file, forse protetto?
             errore 3 (non errore) il file e' vuoto
          */
          printf("Errore %d, file %s; SALTATO\n",err,namelist[i]->d_name);
        }
        else {
          Ng++;
        };
        close(ifp);
      };
    i++;
  };

  free(tmp_nome);
  printf("sono qui fine di carica file grandi \n");
  return 1;
}


int main( int   argc, 
          char *argv[] )
{
  char *direct;
  int i;
  int numero;
  /*int window;*/
  char *pic;
  char *gra;

  direct = (char *) calloc(LUNGPATHNOME,sizeof(char));

  pic = (char *) calloc(LUNGPATHNOME,sizeof(char));
  gra = (char *) calloc(LUNGPATHNOME,sizeof(char));
  RIS = (char *) calloc(LUNGPATHNOME,sizeof(char));
  numero = (int *) malloc(sizeof(int));

  //printf("\nInserisci dimensione dei file\n" );
  fflush(0);
  //while( scanf("%d",numero)  < 0 );
  numero=atoi(argv[1]);
  GRANDE = numero;
  DIMENSIONE = numero;
  printf("\nnumero = %d, string %s", numero,argv[2] );
  //printf("\nInserisci dimensione dei PICCOLI\n" );

  /*while( scanf("%d",numero)  < 0 );*/
  PICCOLO = numero;


  if( PICCOLO > MAX_WIN ) {
    PICCOLO = MAX_WIN;
  };
  if( GRANDE > MAX_WIN ) {
    GRANDE = MAX_WIN;
  };
  
  sprintf(gra,"%d",GRANDE);
  sprintf(pic,"%d",PICCOLO);
  strcat(RIS,"ris_bcl+");
  strcat(RIS,gra);
  strcat(RIS,"-");
  strcat(RIS,pic);
  direct=argv[2];
  /*  strcpy(direct,"/home/dario/Tree/");*/
  //printf("Inserisci directory dei file \n");
  //while( scanf("%s",direct)  < 0 );
  i = (int) strlen(direct);
  if( memcmp(direct+i,"/",1) != 0 ) {
    strcat(direct,"/");
  };
  /*printf("Inserisci dimensione della finestra \n");
    scanf("%d",&window);*/
  carica_file_g(direct);

  printf("\nCaricati i file grandi.");
  calcola();
	printf("\nfine di calcola\n");
  //  free(direct);
  return 1;
}
