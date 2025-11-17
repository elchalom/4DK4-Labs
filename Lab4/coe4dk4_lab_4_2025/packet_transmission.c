
/*
 * Simulation_Run of the ALOHA Protocol
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA
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

#include <stdio.h>
#include <math.h>
#include "trace.h"
#include "output.h"
#include "channel.h"
#include "packet_transmission.h"
#include "data_transmission.h"

/*******************************************************************************/

long int
schedule_transmission_start_event(Simulation_Run_Ptr simulation_run,
				  Time event_time,
				  void * packet) 
{
  Event event;

  event.description = "Start Of Packet";
  event.function = transmission_start_event;
  event.attachment = packet;

  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/*******************************************************************************/

void
transmission_start_event(Simulation_Run_Ptr simulation_run, void * ptr)
{
  Packet_Ptr this_packet;
  Simulation_Run_Data_Ptr data;
  Channel_Ptr channel;

  this_packet = (Packet_Ptr) ptr;
  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  channel = data->channel;

  /* This packet is starting to transmit. */
  increment_transmitting_stn_count(channel);
  this_packet->status = TRANSMITTING;

  if(get_channel_state(channel) != IDLE) {
    /* The channel is now colliding. */
    set_channel_state(channel, COLLISION);
  } else {
    /* The channel is successful, for now. */
    set_channel_state(channel, SUCCESS);
  }

  /* Schedule the end of packet transmission event - reservation mini-slot ends at slot boundary */
  schedule_transmission_end_event(simulation_run,
              SLOT_DURATION_XR * (floor(simulation_run_get_time(simulation_run) / SLOT_DURATION_XR) + 1.0),
              (void *) this_packet);
}

/*******************************************************************************/

long int
schedule_transmission_end_event(Simulation_Run_Ptr simulation_run,
				Time event_time,
				void * packet)
{
  Event event;

  event.description = "End of Packet";
  event.function = transmission_end_event;
  event.attachment = packet;

  return simulation_run_schedule_event(simulation_run, event, event_time);
}

/*******************************************************************************/

void
transmission_end_event(Simulation_Run_Ptr simulation_run, void * packet)
{
  Packet_Ptr this_packet, next_packet;
  Buffer_Ptr buffer, data_buffer;
  Time backoff_duration, now, next_slot;
  Simulation_Run_Data_Ptr data;
  Channel_Ptr channel;

  this_packet = (Packet_Ptr) packet;
  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  channel = data->channel;
  data_buffer = data->data_channel_queue;

  now = simulation_run_get_time(simulation_run);

  /* This station has stopped transmitting on reservation channel. */
  decrement_transmitting_stn_count(channel);

  /* Check if the reservation was successful or collided. */
  if(get_channel_state(channel) == COLLISION) {
    /* The reservation collided. */
    this_packet->collision_count++;
    this_packet->status = WAITING;
    data->number_of_collisions++;

    /* Binary exponential backoff for slotted ALOHA (multiples of slot duration) */
    backoff_duration = SLOT_DURATION_XR * floor(uniform_generator() * pow(2.0, this_packet->collision_count));
    
    /* Calculate next slot boundary after backoff */
    next_slot = SLOT_DURATION_XR * (floor((now + backoff_duration) / SLOT_DURATION_XR) + 1.0);
    
    schedule_transmission_start_event(simulation_run, next_slot, (void *) this_packet);
  } else {
    // The reservation was successful - place packet in FCFS data channel queue
    Station_Ptr station;
    station = data->stations + this_packet->station_id;

    TRACE(printf("Reservation successful. Queueing for data transmission.\n"););

    // Remove the packet from the station buffer
    buffer = station->buffer;
    fifoqueue_get(buffer);

    // Add to data channel queue
    fifoqueue_put(data_buffer, (void *) this_packet);

    // If data channel is idle, start transmission immediately
    if(get_channel_state(data->data_channel) == IDLE && 
       fifoqueue_size(data_buffer) == 1) {
      fifoqueue_get(data_buffer);  // Remove from queue to start transmission
      schedule_data_transmission_start_event(simulation_run, now, (void *) this_packet);
    }

    // See if there is another packet at this station ready to reserve
    if(fifoqueue_size(buffer) > 0) {
      next_packet = (Packet_Ptr) fifoqueue_see_front(buffer);
      
      // Calculate next slot boundary
      next_slot = SLOT_DURATION_XR * (floor(now / SLOT_DURATION_XR) + 1.0);
      
      schedule_transmission_start_event(simulation_run, next_slot, (void *) next_packet);
    }
  }

  /* Clean up the channel state. */
  if(get_transmitting_stn_count(channel) > 0) {
    set_channel_state(channel, COLLISION);
  } else {
    set_channel_state(channel, IDLE);
  }
}



