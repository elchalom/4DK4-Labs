#include <math.h>
#include <stdio.h>
#include "main.h"
#include "packet_transmission.h"
#include "voice_data_arrival.h"

extern double DATA_ARRIVAL_RATE;

/* Schedule voice packet arrival */
long int schedule_voice_arrival_event(Simulation_Run_Ptr simulation_run, double event_time)
{
  Event event;
  event.description = "Voice Packet Arrival";
  event.function = voice_arrival_event;
  event.attachment = (void *) NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/* Schedule data packet arrival */
long int schedule_data_arrival_event(Simulation_Run_Ptr simulation_run, double event_time)
{
  Event event;
  event.description = "Data Packet Arrival";
  event.function = data_arrival_event;
  event.attachment = (void *) NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/* Voice packet arrival event - fixed intervals */
void voice_arrival_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr new_packet;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data->voice_arrival_count++;

  new_packet = (Packet_Ptr) xmalloc(sizeof(Packet));
  new_packet->arrive_time = simulation_run_get_time(simulation_run);
  new_packet->service_time = exponential_generator(MEAN_SERVICE_TIME);
  new_packet->packet_type = VOICE_PACKET;
  new_packet->status = WAITING;

  /* Queue in voice buffer or start transmission */
  if(server_state(data->link) == BUSY) {
    fifoqueue_put(data->voice_buffer, (void*) new_packet);
  } else {
    start_transmission_on_link(simulation_run, new_packet, data->link);
  }

  /* Schedule next voice arrival (fixed interval) */
  schedule_voice_arrival_event(simulation_run,
    simulation_run_get_time(simulation_run) + VOICE_ARRIVAL_INTERVAL);
}

/* Data packet arrival event - Poisson process */
void data_arrival_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr new_packet;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data->data_arrival_count++;

  new_packet = (Packet_Ptr) xmalloc(sizeof(Packet));
  new_packet->arrive_time = simulation_run_get_time(simulation_run);
  new_packet->service_time = exponential_generator(MEAN_SERVICE_TIME);
  new_packet->packet_type = DATA_PACKET;
  new_packet->status = WAITING;

  /* Queue in data buffer or start transmission (if no voice packets waiting) */
  if(server_state(data->link) == BUSY) {
    fifoqueue_put(data->data_buffer, (void*) new_packet);
  } else {
    /* Only start if no voice packets are waiting */
    if(fifoqueue_size(data->voice_buffer) == 0) {
      start_transmission_on_link(simulation_run, new_packet, data->link);
    } else {
      fifoqueue_put(data->data_buffer, (void*) new_packet);
    }
  }

  /* Schedule next data arrival (exponential intervals) */
  schedule_data_arrival_event(simulation_run,
    simulation_run_get_time(simulation_run) + exponential_generator(1.0/DATA_ARRIVAL_RATE));
}