
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
  Simulation_Run_Data_Ptr data;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  /* Clean up all three buffers */
  while (fifoqueue_size(data->buffer1) > 0)
    xfree(fifoqueue_get(data->buffer1));
  xfree(data->buffer1);

  while (fifoqueue_size(data->buffer2) > 0)
    xfree(fifoqueue_get(data->buffer2));
  xfree(data->buffer2);

  while (fifoqueue_size(data->buffer3) > 0)
    xfree(fifoqueue_get(data->buffer3));
  xfree(data->buffer3);

  /* Clean up all three links */
  if (server_state(data->link1) == BUSY)
    xfree(server_get(data->link1));
  xfree(data->link1);

  if (server_state(data->link2) == BUSY)
    xfree(server_get(data->link2));
  xfree(data->link2);

  if (server_state(data->link3) == BUSY)
    xfree(server_get(data->link3));
  xfree(data->link3);

  simulation_run_free_memory(simulation_run);
}

/* New cleanup function for Part 5 */
void
cleanup_memory_part5 (Simulation_Run_Ptr simulation_run)
{
  cleanup_memory(simulation_run); /* Use the same cleanup */
}



