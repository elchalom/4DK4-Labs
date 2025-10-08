#include <math.h>
#include <stdio.h>
#include "main.h"
#include "packet_transmission.h"
#include "network_arrival.h"

extern double P12;

/* Schedule arrival events for all three switches */
long int schedule_switch1_arrival_event(Simulation_Run_Ptr simulation_run, double event_time)
{
  Event event;
  event.description = "Switch 1 Arrival";
  event.function = switch1_arrival_event;
  event.attachment = (void *) NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

long int schedule_switch2_arrival_event(Simulation_Run_Ptr simulation_run, double event_time)
{
  Event event;
  event.description = "Switch 2 Arrival";
  event.function = switch2_arrival_event;
  event.attachment = (void *) NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

long int schedule_switch3_arrival_event(Simulation_Run_Ptr simulation_run, double event_time)
{
  Event event;
  event.description = "Switch 3 Arrival";
  event.function = switch3_arrival_event;
  event.attachment = (void *) NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/* Switch 1 arrival event */
void switch1_arrival_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr new_packet;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data->arrival_count[0]++;

  new_packet = (Packet_Ptr) xmalloc(sizeof(Packet));
  new_packet->arrive_time = simulation_run_get_time(simulation_run);
  new_packet->service_time = LINK1_XMT_TIME;
  new_packet->origin_switch = SWITCH1;
  new_packet->status = WAITING;
  
  /* Decide destination based on probability P12 */
  if (uniform_generator() < P12) {
    new_packet->destination_link = LINK2;
  } else {
    new_packet->destination_link = LINK3;
  }

  /* Queue at Switch 1 or start transmission on Link 1 */
  if(server_state(data->link1) == BUSY) {
    fifoqueue_put(data->buffer1, (void*) new_packet);
  } else {
    start_transmission_on_link1(simulation_run, new_packet);
  }

  /* Schedule next arrival */
  schedule_switch1_arrival_event(simulation_run,
    simulation_run_get_time(simulation_run) + exponential_generator(1.0/LAMBDA1));
}

/* Switch 2 arrival event */
void switch2_arrival_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr new_packet;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data->arrival_count[1]++;

  new_packet = (Packet_Ptr) xmalloc(sizeof(Packet));
  new_packet->arrive_time = simulation_run_get_time(simulation_run);
  new_packet->service_time = LINK2_XMT_TIME;
  new_packet->origin_switch = SWITCH2;
  new_packet->destination_link = LINK2;
  new_packet->status = WAITING;

  /* Queue at Switch 2 or start transmission on Link 2 */
  if(server_state(data->link2) == BUSY) {
    fifoqueue_put(data->buffer2, (void*) new_packet);
  } else {
    start_transmission_on_link2(simulation_run, new_packet);
  }

  /* Schedule next arrival */
  schedule_switch2_arrival_event(simulation_run,
    simulation_run_get_time(simulation_run) + exponential_generator(1.0/LAMBDA2));
}

/* Switch 3 arrival event */
void switch3_arrival_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr new_packet;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data->arrival_count[2]++;

  new_packet = (Packet_Ptr) xmalloc(sizeof(Packet));
  new_packet->arrive_time = simulation_run_get_time(simulation_run);
  new_packet->service_time = LINK3_XMT_TIME;
  new_packet->origin_switch = SWITCH3;
  new_packet->destination_link = LINK3;
  new_packet->status = WAITING;

  /* Queue at Switch 3 or start transmission on Link 3 */
  if(server_state(data->link3) == BUSY) {
    fifoqueue_put(data->buffer3, (void*) new_packet);
  } else {
    start_transmission_on_link3(simulation_run, new_packet);
  }

  /* Schedule next arrival */
  schedule_switch3_arrival_event(simulation_run,
    simulation_run_get_time(simulation_run) + exponential_generator(1.0/LAMBDA3));
}