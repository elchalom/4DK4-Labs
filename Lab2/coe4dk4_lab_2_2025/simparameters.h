
/*
 * 
 * Simulation of A Single Server Queueing System
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

#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

/******************************************************************************/

/* Link and packet parameters */
#define LINK_BIT_RATE 1e6 /* 1 Mbps */
#define VOICE_PACKET_SIZE 1776 /* bits (160 bytes payload + 62 bytes header) */
#define DATA_PACKET_SIZE 1000 /* bits - can be adjusted */

/* Voice traffic parameters */
#define VOICE_ARRIVAL_INTERVAL 0.1 /* 20 ms = 0.02 seconds */
#define MEAN_SERVICE_TIME 0.04 /* 40 ms = 0.04 seconds */

/* Simulation parameters */
#define RUNLENGTH 10000 /* packets - reduced for faster simulation */
#define STEP 50 /* data arrival rate step */

/* Comma separated list of random seeds to run. */
#define RANDOM_SEED_LIST 400474322, 400430923, 12345678, 987654321, 45671234

/* Transmission times */
#define VOICE_XMT_TIME ((double) VOICE_PACKET_SIZE/LINK_BIT_RATE)
#define DATA_XMT_TIME ((double) DATA_PACKET_SIZE/LINK_BIT_RATE)
#define BLIPRATE (RUNLENGTH/1000)

/******************************************************************************/

#endif /* simparameters.h */



