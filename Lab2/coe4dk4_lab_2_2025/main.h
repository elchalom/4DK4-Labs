
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

#ifndef _MAIN_H_
#define _MAIN_H_

/******************************************************************************/

#include "simlib.h"
#include "simparameters.h"

/******************************************************************************/

extern double DATA_ARRIVAL_RATE;

typedef enum {VOICE_PACKET, DATA_PACKET} Packet_Type;

/******************************************************************************/

typedef struct _simulation_run_data_ 
{
  Fifoqueue_Ptr voice_buffer;  /* Priority queue for voice packets */
  Fifoqueue_Ptr data_buffer;   /* Secondary queue for data packets */
  Server_Ptr link;             /* Single transmission link */
  
  long int blip_counter;
  
  /* Voice traffic statistics */
  long int voice_arrival_count;
  long int voice_processed_count;
  double voice_accumulated_delay;
  
  /* Data traffic statistics */
  long int data_arrival_count;
  long int data_processed_count;
  double data_accumulated_delay;
  
  unsigned random_seed;
} Simulation_Run_Data, * Simulation_Run_Data_Ptr;

typedef enum {XMTTING, WAITING} Packet_Status;

typedef struct _packet_ 
{
  double arrive_time;
  double service_time;
  Packet_Type packet_type;  /* VOICE_PACKET or DATA_PACKET */
  Packet_Status status;
} Packet, * Packet_Ptr;

/*
 * Function prototypes
 */

int main(void);

/******************************************************************************/

#endif /* main.h */


