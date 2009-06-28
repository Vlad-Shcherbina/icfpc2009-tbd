#include <stdio.h>
#include <math.h>

#define SIZE	16384
#ifndef MAX_STEPS
#define MAX_STEPS 3000000
#endif

double mu;

extern double task;
extern double ports_in[SIZE], ports_out[SIZE];
extern unsigned int verbose;
extern unsigned int iterations;

int process();
void hohmann_step( int *state, double x, double y, double fuel, double rt, double *dvx, double *dvy );

int do_problem()
{
	mu = 6.67428 * 6.0 * pow(10,13);
	if( iterations == 1 )
		iterations = MAX_STEPS;
	/* hohmann */
	if( task < 2000.0 )
	{
		unsigned int step;
		int state = 0;
		for( step = 0; step < iterations; step++ )
		{
			ports_in[0x3E80] = task;
			process();
			hohmann_step( &state, ports_out[0x02], ports_out[0x03], ports_out[0x01], ports_out[0x04], ports_in+2, ports_in+3 );
			printf( "%f %f\n", ports_out[0x02], ports_out[0x03] );
			if( ports_out[0] != 0.0 )
			{
				fprintf( stderr, "score %f at step %u\n", ports_out[0], step );
				return 1;
			}
		}
	}

	return 0;
}

/* per-frame orbit transfer */
void hohmann_step( int *state, double x, double y, double fuel, double rt, double *dvx, double *dvy )
{
	static double px = 0.0, py = 0.0, rp = 0.0;
	double rc = sqrt( x*x + y*y );
	static double ro = 0.0;
	*dvx = *dvy = 0.0;
	switch( *state )
	{
		case 0: /* get the direction */
			ro = rc;
			*state = 1;
			fprintf( stderr, "need: %f -> %f\n", rc, rt );
			break;
		case 1: /* first impulse */
			{
				double vx = x-px;
				double vy = y-py;
				if( verbose ) fprintf( stderr, "vx=%f, vy=%f\n", vx, vy );
				double n = sqrt( vx*vx + vy*vy );
				double dv = sqrt( mu / rc ) * ( sqrt(2.0*rt/(rc+rt)) - 1.0 ) / n;
				*dvx = - dv * vx;
				*dvy = - dv * vy;
				if( verbose ) fprintf( stderr, "dvx=%f, dvy=%f\n", *dvx, *dvy );
			}
			*state = 2;
			break;
		case 2: /* wait for the orbit */
			if( rc < rp )
			{
				double vx = x-px;
				double vy = y-py;
				if( verbose ) fprintf( stderr, "vx=%f, vy=%f\n", vx, vy );
				double n = sqrt( vx*vx + vy*vy );
				double dv = sqrt( mu / rt ) * ( 1.0 - sqrt(2.0*ro/(ro+rt)) ) / n;
				*dvx = - dv * vx;
				*dvy = - dv * vy;
				if( verbose ) fprintf( stderr, "dvx=%f, dvy=%f\n", *dvx, *dvy );
				*state = 3;
			}
			rp = rc;
			break;
		default: /* complete */
			if( verbose > 1 )
				fprintf( stderr, "d = %f\n", rc-rt );
			break;
	}
	if( verbose > 2 )
		fprintf( stderr, "%u, f=%f, r=%f, rt=%f, vx = %f, vy = %f, dvx = %f, dvy = %f\n", *state, fuel, rc, rt, x-px, y-py, *dvx, *dvy );
	px = x;
	py = y;
}
