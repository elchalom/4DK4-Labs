
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

/* ===== NEW: toggle service-time model =====
 * 0 => M/D/1 (deterministic service time = SERVICE_TIME)
 * 1 => M/M/1 (exponential service time with mean = SERVICE_TIME)
 */
#define SERVICE_DIST_MM1 1
/*******************************************************************************/

/*
 * Simulation Parameters
 */

#define RANDOM_SEED 5259140
#define NUMBER_TO_SERVE 50e6

#define SERVICE_TIME 10
#define ARRIVAL_RATE 0.1

#define BLIP_RATE 10000

/* NEW */
#define MAX_QUEUE_SIZE 50  

/*******************************************************************************/

typedef struct {
  double utilization;
  double fraction_served;
  double mean_number_in_system;
  double mean_delay;
  long int total_served;
  long int total_arrived;
  double clock_time;
  double rejection_probability;
  long int rejected_customers;
} Results;

/* ===== NEW: helper to draw a service time according to the selected model ===== */
static inline double draw_service_time(void) {
#if SERVICE_DIST_MM1
  /* M/M/1: exponential with mean = SERVICE_TIME */
  return exponential_generator((double) SERVICE_TIME);
#else
  /* M/D/1: deterministic service time */
  return (double) SERVICE_TIME;
#endif
}

/* Run one simulation for a given arrival rate, seed, and verbosity. */
static Results run_one(double arrival_rate, unsigned seed, int verbose)
{
  Results r;

  double clock = 0; /* Clock keeps track of simulation time. */

  /* System state variables. */
  int number_in_system = 0;
  double next_arrival_time = 0;
  double next_departure_time = 0;

  /* ===== NEW: track the duration of the job currently in service ===== */
  double current_service_time = 0.0;

  /* Data collection variables. */
  long int total_served = 0;
  long int total_arrived = 0;

  long int rejected_customers = 0;

  double total_busy_time = 0;
  double integral_of_n = 0;
  double last_event_time = 0;

  random_generator_initialize(seed);

  while (total_served < NUMBER_TO_SERVE) {

    if (number_in_system == 0 || next_arrival_time < next_departure_time) {
      /* Arrival */
      clock = next_arrival_time;
      next_arrival_time = clock + exponential_generator((double) (1.0/arrival_rate));

      /* Stats update */
      integral_of_n += number_in_system * (clock - last_event_time);
      last_event_time = clock;

      // Check if queue is full (number_in_system includes customer in service)
      if (number_in_system >= MAX_QUEUE_SIZE + 1) {
        // Reject this customer
        rejected_customers++;
        total_arrived++;
        // Do NOT increment number_in_system, do NOT start service
      } else {
        number_in_system++;
        total_arrived++;

        /* If the system was idle, start service immediately. */
        if (number_in_system == 1) {
          current_service_time = draw_service_time();
          next_departure_time = clock + current_service_time;
        }
      }

    } else {
      /* Departure */
      clock = next_departure_time;

      /* Stats update */
      integral_of_n += number_in_system * (clock - last_event_time);
      last_event_time = clock;

      number_in_system--;
      total_served++;

      /* ===== CHANGED: busy time is the actual service duration ===== */
      total_busy_time += current_service_time;

      if (number_in_system > 0) {
        /* Start next job immediately, draw a fresh service time */
        current_service_time = draw_service_time();               /* NEW */
        next_departure_time = clock + current_service_time;       /* CHANGED */
      } else {
        /* Idle */
        current_service_time = 0.0;                               /* NEW (optional) */
      }

      if (verbose && total_served % BLIP_RATE == 0)
        printf("Customers served = %ld (Total arrived = %ld)\r", total_served, total_arrived);
    }
  }

  /* Results */
  r.utilization = total_busy_time/clock;
  r.fraction_served = (double) total_served/total_arrived;
  r.mean_number_in_system = integral_of_n/clock;
  r.mean_delay = integral_of_n/total_served; /* Little’s law-based estimator of total time in system */
  r.total_served = total_served;
  r.total_arrived = total_arrived;
  r.clock_time = clock;
  r.rejection_probability = (double) rejected_customers / (double) total_arrived;
  r.rejected_customers = rejected_customers;
  return r;
}

int main()
{
  setvbuf(stdout, NULL, _IONBF, 0);

  const double rates[] = {0.01, 0.03, 0.05, 0.07, 0.08, 0.09, 0.098};
  const int NRATES = (int)(sizeof(rates)/sizeof(rates[0]));

  const unsigned seeds[10] = {
    400430923u, 400474322u, 89101112u, 424242u, 8675309u,
    1357911u, 24681012u, 31415926u, 27182818u, 16180339u
  };

  /* Print header and a tag telling which model this build is */
#if SERVICE_DIST_MM1
  printf("# model=M/M/1\n");
#else
  printf("# model=M/D/1\n");
#endif
  // printf("arrival_rate,seed,utilization,fraction_served,mean_number_in_system,mean_delay,total_served,total_arrived,clock_time,rejection_probability,rejected_customers\n");
  printf("arrival_rate\tseed\tutilization\tfraction_served\tmean_number_in_system\tmean_delay\ttotal_served\ttotal_arrived\tclock_time\trejection_probability\trejected_customers\n");
  int i, s;
  for (i = 0; i < NRATES; i++) {
    double rate = rates[i];
    double sum_mean_delay = 0.0;

    for (s = 0; s < 10; s++) {
      Results r = run_one(rate, seeds[s], 0 /* verbose */);
      sum_mean_delay += r.mean_delay;

      // printf("%.5f,%u,%.10f,%.10f,%.10f,%.10f,%ld,%ld,%.10f\n",
      printf("%.5f\t%u\t%.10f\t%.10f\t%.10f\t%.10f\t%ld\t%ld\t%.10f\t%.10f\t%ld\n",
             rate, seeds[s], r.utilization, r.fraction_served,
             r.mean_number_in_system, r.mean_delay,
             r.total_served, r.total_arrived, r.clock_time,
             r.rejection_probability, r.rejected_customers);
      fflush(stdout);
    }

    double avg_mean_delay = sum_mean_delay / 10.0;
    printf("AVG\t%.5f\t%d_seeds\tavg_mean_delay\t%.10f\n", rate, 10, avg_mean_delay);
    fflush(stdout);
    fprintf(stderr, "Completed arrival_rate=%.5f\n", rate);
  }
  return 0;
}

//   /* Print TSV header (tab-delimited for robust Excel import) */
//   printf("arrival_rate\tseed\tutilization\tfraction_served\tmean_number_in_system\tmean_delay\ttotal_served\ttotal_arrived\tclock_time\n");
//   {
//     int i, s;
//     for (i = 0; i < NRATES; i++) {
//     double rate = rates[i];
//     double sum_mean_delay = 0.0;

//       for (s = 0; s < 10; s++) {
//       Results r = run_one(rate, seeds[s], 0 /* verbose */);
//       sum_mean_delay += r.mean_delay;

//       /* Per-run TSV row (tab-delimited, CRLF line ending) */
//       printf("%.5f\t%u\t%.10f\t%.10f\t%.10f\t%.10f\t%ld\t%ld\t%.10f\n",
//              rate, seeds[s], r.utilization, r.fraction_served,
//              r.mean_number_in_system, r.mean_delay,
//              r.total_served, r.total_arrived, r.clock_time);
//       fflush(stdout);
//       }

//   /* Per-rate average summary row (prefixed with AVG for easy filtering). */
//     double avg_mean_delay = sum_mean_delay / 10.0;
//   printf("AVG\t%.5f\t%d_seeds\tavg_mean_delay\t%.10f\n", rate, 10, avg_mean_delay);
//     fflush(stdout);

//     /* Progress message to stderr so it doesn't pollute CSV. */
//     fprintf(stderr, "Completed arrival_rate=%.5f\n", rate);
//     }
//   }
//   return 0;
// }
// */