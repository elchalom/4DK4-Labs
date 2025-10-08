/*
 * 
 * Simulation_Run of A Single Server Queueing System
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA,
 * todd@mcmaster.ca
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
 */

/*******************************************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "output.h"
#include "simparameters.h"
#include "packet_arrival.h"
#include "cleanup_memory.h"
#include "trace.h"
#include "main.h"
#include "network_arrival.h"

/******************************************************************************/

/*
 * main.c declares and creates a new simulation_run with parameters defined in
 * simparameters.h. The code creates a fifo queue and server for the single
 * server queueuing system. It then loops through the list of random number
 * generator seeds defined in simparameters.h, doing a separate simulation_run
 * run for each. To start a run, it schedules the first packet arrival
 * event. When each run is finished, output is printed on the terminal.
 *
 * This modified version sweeps PACKET_ARRIVAL_RATE over a range of values,
 * runs the simulation for each, and outputs results to a CSV file for plotting.
 */

/******************************************************************************/

/* Declare PACKET_ARRIVAL_RATE as a global variable */
double PACKET_ARRIVAL_RATE;
double P12; // Global probability variable

/* 
 * Main function: sweeps arrival rates, runs simulation for each, and outputs results to CSV.
 */
int main(void)
{
    Simulation_Run_Ptr simulation_run;
    Simulation_Run_Data data;

    /* Open CSV file for writing results */
    FILE *csv = fopen("data/results.csv", "w");
    if (!csv) {
        perror("Failed to open results.csv");
        return 1;
    }
    
    /* Write CSV header */
    fprintf(csv, "p12,seed,switch1_mean_delay,switch2_mean_delay,switch3_mean_delay\n");

    /* Sweep P12 from 0.1 to 0.9 in steps of 0.1 */
    for (double p = 0.1; p <= 0.9; p += 0.1) {
        P12 = p;
        
        /* Run simulation with different random seeds */
        unsigned RANDOM_SEEDS[] = {RANDOM_SEED_LIST, 0};
        unsigned random_seed;
        int j = 0;

        while ((random_seed = RANDOM_SEEDS[j++]) != 0) {
            /* Create a new simulation run */
            simulation_run = simulation_run_new();
            simulation_run_attach_data(simulation_run, (void *)&data);

            /* Initialize data structures */
            data.blip_counter = 0;
            data.random_seed = random_seed;
            
            for(int i = 0; i < 3; i++) {
                data.arrival_count[i] = 0;
                data.processed_count[i] = 0;
                data.accumulated_delay[i] = 0.0;
            }

            /* Create buffers and links */
            data.buffer1 = fifoqueue_new();
            data.buffer2 = fifoqueue_new();
            data.buffer3 = fifoqueue_new();
            data.link1 = server_new();
            data.link2 = server_new();
            data.link3 = server_new();

            /* Set random seed */
            random_generator_initialize(random_seed);

            /* Schedule initial arrivals for all switches */
            schedule_switch1_arrival_event(simulation_run, 0.0);
            schedule_switch2_arrival_event(simulation_run, 0.0);
            schedule_switch3_arrival_event(simulation_run, 0.0);

            /* Run simulation until enough packets processed */
            long total_processed = 0;
            while (total_processed < RUNLENGTH) {
                simulation_run_execute_event(simulation_run);
                total_processed = data.processed_count[0] + data.processed_count[1] + data.processed_count[2];
            }

            /* Calculate mean delays and output to CSV */
            double mean_delay[3];
            for(int i = 0; i < 3; i++) {
                mean_delay[i] = (data.processed_count[i] > 0) ? 
                    1000.0 * data.accumulated_delay[i] / data.processed_count[i] : 0.0;
            }
            
            fprintf(csv, "%.1f,%d,%.3f,%.3f,%.3f\n", 
                P12, random_seed, mean_delay[0], mean_delay[1], mean_delay[2]);

            /* Clean up */
            cleanup_memory_part5(simulation_run);
        }
    }

    fclose(csv);
    return 0;
}