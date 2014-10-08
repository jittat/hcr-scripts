#include <cstdio>
#include <cmath>
#include <cstdlib>

using namespace std;

#define MAX_N 500
#define INFTY 10000
#define MAX_DISTANCE 10000
#define DIST_SCALE 0.009041543572655762

int n,m;
double d[MAX_N][MAX_N];
double x[MAX_N], y[MAX_N];
bool is_station[MAX_N];
double dist_bound;

double distance(double sx, double sy, double tx, double ty)
{
  return sqrt((sx-tx)*(sx-tx) + (sy-ty)*(sy-ty));
}

void read_graph(char* fname, double dbound)
{
  FILE* fp = fopen(fname, "r");
  char buff[100];
  fscanf(fp,"%d %d",&n,&m);

  for(int i=0; i<n; i++)
    for(int j=0; j<n; j++)
      d[i][j] = INFTY;
  
  for(int i=0; i<n; i++) {
    int j,f;
    fscanf(fp,"%d %d %s %lf %lf",&j,&f,buff,&x[i],&y[i]);
    is_station[i] = (f == 1);
  }

  for(int i=0; i<m; i++) {
    int u,v;
    double dd;
    fscanf(fp,"%d %d %lf", &u, &v, &dd);
    d[u][v] = dd;
    d[v][u] = dd;
  }

  for(int i=0; i<n; i++)
    for(int j=0; j<n; j++)
      if((d[i][j] >= INFTY-0.1) && (is_station[i]) && (is_station[j])) {
        double dist = distance(x[i],y[i],x[j],y[j]);
        if(dist < dbound)
          d[i][j] = dist;
      }
  
  fclose(fp);
}

void asap()
{
  for(int k=0; k < n; k++)
    for(int i=0; i < n; i++)
      for(int j=0; j < n; j++)
        if(d[i][k] + d[k][j] < d[i][j]) {
          d[i][j] = d[i][k] + d[k][j];
        }
}

double dstart[MAX_N];
double dterm[MAX_N];

double network_distance(double sx, double sy, double tx, double ty, double dbound)
{
  for(int i=0; i<n; i++) {
    if(is_station[i]) {
      dstart[i] = distance(sx,sy,x[i],y[i]);
      dterm[i] = distance(x[i],y[i],tx,ty);
      if(dstart[i] > dbound)
        dstart[i] = INFTY + 1;
      if(dterm[i] > dbound)
        dterm[i] = INFTY + 1;
    } else {
      dstart[i] = INFTY + 1;
      dterm[i] = INFTY + 1;
    }
  }

  double mind = INFTY;
  for(int i=0; i<n; i++) {
    if(!is_station[i])
      continue;

    double d1 = dstart[i];
    if(d1 > mind)
      continue;
    
    for(int j=0; j<n; j++) {
      if((j==i) || (!is_station[j]))
        continue;

      double dd = (d1 + d[i][j]);
      if(dd > mind)
        continue;

      dd += dterm[j];
      if(dd < mind) {
        //printf("%d,%d,%lf\n",i,j,d[i][j]);
        mind = dd;
      }
    }
  }
  return mind;
}

void process(char* fname, double dbound)
{
  FILE* fp = fopen(fname,"r");
  int k;
  fscanf(fp,"%d",&k);
  for(int i=0; i<k; i++) {
    double sx,sy,tx,ty;
    fscanf(fp,"%lf,%lf,%lf,%lf",&sx,&sy,&tx,&ty);
    double direct_distance = distance(sx,sy,tx,ty);
    double net_distance = network_distance(sx,sy,tx,ty,dbound);
    printf("%lf %lf\n", direct_distance, net_distance);
  }
  fclose(fp);
}

main(int argc, char* argv[])
{
  if(argc==4)
    dist_bound = atof(argv[3]) * DIST_SCALE;
  else
    dist_bound = MAX_DISTANCE;
  read_graph(argv[1], dist_bound);
  asap();
  process(argv[2], dist_bound);
}

