
/*
 *
 * Simulation of Single Server Queueing System
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA,
 * todd@mcmaster.ca
 * 
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation; either version 3 of the License, or (at your option) any later
 * version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
 */

/*******************************************************************************/

#include <stdio.h>
#include "simlib.h"

/*******************************************************************************/

/*
 * Simulation Parameters
 */

#define RANDOM_SEED 5259140
#define NUMBER_TO_SERVE 50e6

#define SERVICE_TIME 10
#define ARRIVAL_RATE 0.1

#define BLIP_RATE 10000

/*******************************************************************************/

/*
 * main() uses various simulation parameters and creates a clock variable to
 * simulate real time. A loop repeatedly determines if the next event to occur
 * is a customer arrival or customer departure. In either case the state of the
 * system is updated and statistics are collected before the next
 * iteration. When it finally reaches NUMBER_TO_SERVE customers, the program
 * outputs some statistics such as mean delay.
 */

/* Results struct for a single simulation run. */
typedef struct {
  double utilization;
  double fraction_served;
  double mean_number_in_system;
  double mean_delay;
  long int total_served;
  long int total_arrived;
  double clock_time;
} Results;

/* Run one simulation for a given arrival rate, seed, and verbosity. */
static Results run_one(double arrival_rate, unsigned seed, int verbose)
{
  Results r;

  double clock = 0; /* Clock keeps track of simulation time. */

  /* System state variables. */
  int number_in_system = 0;
  double next_arrival_time = 0;
  double next_departure_time = 0;

  /* Data collection variables. */
  long int total_served = 0;
  long int total_arrived = 0;

  double total_busy_time = 0;
  double integral_of_n = 0;
  double last_event_time = 0;

  /* Set the seed of the random number generator. */
  random_generator_initialize(seed);

  /* Process customers until we are finished. */
  while (total_served < NUMBER_TO_SERVE) {

    /* Test if the next event is a customer arrival or departure. */
    if(number_in_system == 0 || next_arrival_time < next_departure_time) {

      /* A new arrival is occurring. */

      clock = next_arrival_time;
      next_arrival_time = clock + exponential_generator((double) 1/arrival_rate);

      /* Update our statistics. */
      integral_of_n += number_in_system * (clock - last_event_time);
      last_event_time = clock;

      number_in_system++;
      total_arrived++;

      /* If this customer has arrived to an empty system, start its service right away. */
      if(number_in_system == 1) next_departure_time = clock + SERVICE_TIME;

    } else {

      /* A customer departure is occuring. */

      clock = next_departure_time;

      /* Update our statistics. */
      integral_of_n += number_in_system * (clock - last_event_time);
      last_event_time = clock;

      number_in_system--;
      total_served++;
      total_busy_time += SERVICE_TIME;

      /* If there are other customers waiting, start one in service right away. */
      if(number_in_system > 0) next_departure_time = clock + SERVICE_TIME;

      /* Optional progress blip. Keep quiet for automated runs unless verbose. */
      if (verbose && total_served % BLIP_RATE == 0)
        printf("Customers served = %ld (Total arrived = %ld)\r", total_served, total_arrived);
    }
  }

  /* Populate results (no printing here; caller will handle). */
  r.utilization = total_busy_time/clock;
  r.fraction_served = (double) total_served/total_arrived;
  r.mean_number_in_system = integral_of_n/clock;
  r.mean_delay = integral_of_n/total_served;
  r.total_served = total_served;
  r.total_arrived = total_arrived;
  r.clock_time = clock;
  return r;
}

int main()
{
  /* Disable stdout buffering so redirected CSV writes appear immediately. */
  setvbuf(stdout, NULL, _IONBF, 0);

  /* Define arrival rates: 0.01 to 0.09 (inclusive) step 0.01) */
  const double rates[] = {0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09};
  const int NRATES = (int)(sizeof(rates)/sizeof(rates[0]));

  /* Ten seeds including the student number 400430923. */
  const unsigned seeds[10] = {
    400430923u, 400474322u, 89101112u, 424242u, 8675309u,
    1357911u, 24681012u, 31415926u, 27182818u, 16180339u
  };

  /* Print CSV header. */
  printf("arrival_rate,seed,utilization,fraction_served,mean_number_in_system,mean_delay,total_served,total_arrived,clock_time\n");
  {
    int i, s;
    for (i = 0; i < NRATES; i++) {
    double rate = rates[i];
    double sum_mean_delay = 0.0;

      for (s = 0; s < 10; s++) {
      Results r = run_one(rate, seeds[s], 0 /* verbose */);
      sum_mean_delay += r.mean_delay;

      /* Per-run CSV row */
      printf("%.5f,%u,%.10f,%.10f,%.10f,%.10f,%ld,%ld,%.10f\n",
             rate, seeds[s], r.utilization, r.fraction_served,
             r.mean_number_in_system, r.mean_delay,
             r.total_served, r.total_arrived, r.clock_time);
      fflush(stdout);
      }

    /* Per-rate average summary row (prefixed with AVG for easy filtering). */
    double avg_mean_delay = sum_mean_delay / 10.0;
    printf("AVG,%.5f,%d_seeds,avg_mean_delay,%.10f\n", rate, 10, avg_mean_delay);
    fflush(stdout);

    /* Progress message to stderr so it doesn't pollute CSV. */
    fprintf(stderr, "Completed arrival_rate=%.5f\n", rate);
    }
  }
  return 0;

}






