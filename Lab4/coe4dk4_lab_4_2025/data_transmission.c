/*
 * Data Channel Transmission for Packet Reservation Protocol
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA
 * todd@mcmaster.ca
 */

/*******************************************************************************/

#include <stdio.h>
#include <math.h>
#include "trace.h"
#include "output.h"
#include "channel.h"
#include "data_transmission.h"

/*******************************************************************************/

long int
schedule_data_transmission_start_event(Simulation_Run_Ptr simulation_run,
                                       Time event_time,
                                       void * packet) 
{
  Event event;

  event.description = "Start Of Data Packet";
  event.function = data_transmission_start_event;
  event.attachment = packet;

  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/*******************************************************************************/

void
data_transmission_start_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Packet_Ptr this_packet;
  Simulation_Run_Data_Ptr data;
  Channel_Ptr data_channel;

  this_packet = (Packet_Ptr) ptr;
  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  data_channel = data->data_channel;

  /* This packet is starting to transmit on data channel. */
  increment_transmitting_stn_count(data_channel);
  this_packet->status = TRANSMITTING;
  set_channel_state(data_channel, SUCCESS);

  /* Schedule the end of data packet transmission event. */
  schedule_data_transmission_end_event(simulation_run,
                                       simulation_run_get_time(simulation_run) + 
                                       this_packet->service_time,
                                       (void *) this_packet);
}

/*******************************************************************************/

long int
schedule_data_transmission_end_event(Simulation_Run_Ptr simulation_run,
                                     Time event_time,
                                     void * packet)
{
  Event event;

  event.description = "End of Data Packet";
  event.function = data_transmission_end_event;
  event.attachment = packet;

  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/*******************************************************************************/

void
data_transmission_end_event(Simulation_Run_Ptr simulation_run, void * packet)
{
  Packet_Ptr this_packet, next_packet;
  Buffer_Ptr data_buffer;
  Time now;
  Simulation_Run_Data_Ptr data;
  Channel_Ptr channel;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  channel = data->data_channel;

  now = simulation_run_get_time(simulation_run);

  this_packet = (Packet_Ptr) packet;
  data_buffer = data->data_channel_queue;

  /* This station has stopped transmitting. */
  decrement_transmitting_stn_count(channel);
  set_channel_state(channel, IDLE);

  TRACE(printf("Data transmission success.\n"););

  /* Collect statistics. */
  data->number_of_packets_processed++;

  (data->stations + this_packet->station_id)->packet_count++;
  (data->stations + this_packet->station_id)->accumulated_delay += 
    now - this_packet->arrive_time;

  data->number_of_collisions += this_packet->collision_count;
  data->accumulated_delay += now - this_packet->arrive_time;
  output_blip_to_screen(simulation_run);

  /* This packet is done. */
  xfree((void *) packet);

  /* See if there is another packet in the data channel queue.
     If so, enable it for transmission. We will transmit immediately. */
  if(fifoqueue_size(data_buffer) > 0) {
    next_packet = (Packet_Ptr) fifoqueue_get(data_buffer);
    schedule_data_transmission_start_event(simulation_run, now, (void *) next_packet);
  }
}

/*******************************************************************************/

double
get_data_packet_duration(void)
{
  return exponential_generator((double) MEAN_DATA_PACKET_DURATION);
}

