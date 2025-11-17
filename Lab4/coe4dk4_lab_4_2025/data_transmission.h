/*
 * Data Channel Transmission for Packet Reservation Protocol
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA
 * todd@mcmaster.ca
 */

/*******************************************************************************/

#include "main.h"

/*******************************************************************************/

#ifndef _DATA_TRANSMISSION_H_
#define _DATA_TRANSMISSION_H_

/*******************************************************************************/

/*
 * Function prototypes
 */

void
data_transmission_start_event(Simulation_Run_Ptr, void *);

long int
schedule_data_transmission_start_event(Simulation_Run_Ptr, Time, void *);

void
data_transmission_end_event(Simulation_Run_Ptr, void *);

long int
schedule_data_transmission_end_event(Simulation_Run_Ptr, Time, void *);

double
get_data_packet_duration(void);

/*******************************************************************************/

#endif /* data_transmission.h */