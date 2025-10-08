#ifndef _NETWORK_ARRIVAL_H_
#define _NETWORK_ARRIVAL_H_

#include "simlib.h"

/* Function prototypes */
void switch1_arrival_event(Simulation_Run_Ptr, void*);
void switch2_arrival_event(Simulation_Run_Ptr, void*);
void switch3_arrival_event(Simulation_Run_Ptr, void*);

long schedule_switch1_arrival_event(Simulation_Run_Ptr, double);
long schedule_switch2_arrival_event(Simulation_Run_Ptr, double);
long schedule_switch3_arrival_event(Simulation_Run_Ptr, double);

#endif /* network_arrival.h */