
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

/******************************************************************************/

#include "simlib.h"
#include "main.h"
#include "cleanup_memory.h"

/******************************************************************************/

/*
 * When a simulation_run run is finished, this function cleans up the memory
 * that has been allocated.
 */

void
cleanup_memory (Simulation_Run_Ptr simulation_run)
{
  // Simulation_Run_Data_Ptr data;

  // data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  // /* Clean up buffer */
  // while (fifoqueue_size(data->buffer) > 0)
  //   xfree(fifoqueue_get(data->buffer));
  // xfree(data->buffer);

  // /* Clean up link */
  // if (server_state(data->link) == BUSY)
  //   xfree(server_get(data->link));
  // xfree(data->link);

  // simulation_run_free_memory(simulation_run);
}

/* New cleanup function for Part 5 */
void
cleanup_memory_part5 (Simulation_Run_Ptr simulation_run)
{
  cleanup_memory(simulation_run); /* Use the same cleanup */
}

void
cleanup_memory_part6 (Simulation_Run_Ptr simulation_run)
{
  // Simulation_Run_Data_Ptr data;

  // data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  // /* Clean up buffer */
  // while (fifoqueue_size(data->buffer) > 0)
  //   xfree(fifoqueue_get(data->buffer));
  // xfree(data->buffer);

  // /* Clean up link */
  // if (server_state(data->link) == BUSY)
  //   xfree(server_get(data->link));
  // xfree(data->link);

  // simulation_run_free_memory(simulation_run);
}

void
cleanup_memory_part7 (Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  /* Clean up voice buffer */
  while (fifoqueue_size(data->voice_buffer) > 0)
    xfree(fifoqueue_get(data->voice_buffer));
  xfree(data->voice_buffer);

  /* Clean up data buffer */
  while (fifoqueue_size(data->data_buffer) > 0)
    xfree(fifoqueue_get(data->data_buffer));
  xfree(data->data_buffer);

  /* Clean up link */
  if (server_state(data->link) == BUSY)
    xfree(server_get(data->link));
  xfree(data->link);

  simulation_run_free_memory(simulation_run);
}



