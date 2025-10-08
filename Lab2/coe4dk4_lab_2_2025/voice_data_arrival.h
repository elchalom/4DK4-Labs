#ifndef _VOICE_DATA_ARRIVAL_H_
#define _VOICE_DATA_ARRIVAL_H_

#include "simlib.h"

/* Function prototypes */
void voice_arrival_event(Simulation_Run_Ptr, void*);
void data_arrival_event(Simulation_Run_Ptr, void*);

long schedule_voice_arrival_event(Simulation_Run_Ptr, double);
long schedule_data_arrival_event(Simulation_Run_Ptr, double);

#endif /* voice_data_arrival.h */