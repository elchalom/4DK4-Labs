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
#include "voice_data_arrival.h"

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

double DATA_ARRIVAL_RATE; /* Global variable */

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
    fprintf(csv, "data_arrival_rate,seed,voice_mean_delay,data_mean_delay\n");

    /* Sweep data arrival rates from 50 to 500 packets/sec */
    for (double rate = 1; rate <= 15; rate += 1) {
        DATA_ARRIVAL_RATE = rate;
        
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
            data.voice_arrival_count = 0;
            data.voice_processed_count = 0;
            data.voice_accumulated_delay = 0.0;
            data.data_arrival_count = 0;
            data.data_processed_count = 0;
            data.data_accumulated_delay = 0.0;

            /* Create separate buffers for voice and data, plus link */
            data.voice_buffer = fifoqueue_new();
            data.data_buffer = fifoqueue_new();
            data.link = server_new();

            /* Set random seed */
            random_generator_initialize(random_seed);

            /* Schedule initial arrivals */
            schedule_voice_arrival_event(simulation_run, 0.0);
            schedule_data_arrival_event(simulation_run, 0.0);

            /* Run simulation until enough packets processed */
            long total_processed = 0;
            while (total_processed < RUNLENGTH) {
                simulation_run_execute_event(simulation_run);
                total_processed = data.voice_processed_count + data.data_processed_count;
            }

            /* Calculate mean delays and output to CSV */
            double voice_mean_delay = (data.voice_processed_count > 0) ? 
                1000.0 * data.voice_accumulated_delay / data.voice_processed_count : 0.0;
            double data_mean_delay = (data.data_processed_count > 0) ? 
                1000.0 * data.data_accumulated_delay / data.data_processed_count : 0.0;
            
            fprintf(csv, "%.1f,%d,%.3f,%.3f\n", 
                DATA_ARRIVAL_RATE, random_seed, voice_mean_delay, data_mean_delay);

            /* Clean up */
            cleanup_memory_part7(simulation_run);
        }
    }

    fclose(csv);
    return 0;
}