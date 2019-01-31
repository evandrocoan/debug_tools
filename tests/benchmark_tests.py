#! /usr/bin/env python
# -*- coding: utf-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2019 @ Evandro Coan
#   Benchmark this module versus logging and print methods
#
#  Redistributions of source code must retain the above
#  copyright notice, this list of conditions and the
#  following disclaimer.
#
#  Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials
#  provided with the distribution.
#
#  Neither the name Evandro Coan nor the names of any
#  contributors may be used to endorse or promote products
#  derived from this software without specific prior written
#  permission.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or ( at
#  your option ) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################################
#
import logging
from debug_tools import logger

import sys
import pstats
import cProfile

from io import StringIO

def average(stats, average_count):
    stats.total_calls /= average_count
    stats.prim_calls /= average_count
    stats.total_tt /= average_count

    for func, source in stats.stats.items():
        cc, nc, tt, ct, callers = source
        stats.stats[func] = (cc/average_count, nc/average_count, tt/average_count, ct/average_count, callers)

    return stats

def profile_something(profile_function, average_count, iterations_count):
    output_stream = StringIO()
    profiler_status = pstats.Stats( stream=output_stream )

    for index in range(average_count):
        profiler = cProfile.Profile()
        profiler.enable()

        profile_function( iterations_count )
        profiler.disable()
        profiler_status.add( profiler )

        print( 'Profiled', '{0:7.3f}'.format( profiler_status.total_tt ), 'seconds at', '%3d' % (index + 1),
                'for', profile_function.__name__, flush=True )

    average( profiler_status, average_count )
    profiler_status.sort_stats( "time" )
    profiler_status.print_stats()

    return "\n Profile results for %s\n%s" % ( profile_function.__name__, output_stream.getvalue() ), profiler_status


def run_profiling(first_function, second_function, average_count, iterations_count):
    first_function_results, first_function_stats = profile_something( first_function, average_count, iterations_count )
    second_function_results, second_function_stats = profile_something( second_function, average_count, iterations_count )
    difference = first_function_stats.total_tt - second_function_stats.total_tt

    output = 2500
    output_stream = StringIO()
    print( first_function_results[0:output], file=output_stream )
    print( '\n', second_function_results[0:output], file=output_stream )
    print( '\nTotal difference %.5f' % difference, file=output_stream )

    return ( ( difference, first_function_stats.total_tt, second_function_stats.total_tt,
                first_function.__name__, second_function.__name__, format(iterations_count, ',d') ),
            output_stream.getvalue() )


def get_debug_tools(level=1):
    logger.Debugger.deleteAllLoggers()
    log = logger.getLogger( level, "benchmark", tick=False )
    return log


def get_loggging_debug():
    logging.Logger.manager.loggerDict.clear()
    log = logging.getLogger( "benchmark" )

    if not log.hasHandlers():
        date_format = "%H:%M:%S"
        string_format = "%(asctime)s:%(msecs)010.6f - %(name)s.%(funcName)s:%(lineno)d - %(message)s"

        stream = logging.StreamHandler()
        formatter = logging.Formatter( string_format, date_format )
        stream.setFormatter( formatter )
        log.addHandler( stream )
    return log


def debug_tools_log_debug_off(iterations_count):
    log = get_debug_tools()
    log.setLevel( "WARNING" )

    for index in range( iterations_count ):
        log.debug( 'Message' )

def logging_mod_log_debug_off(iterations_count):
    log = get_loggging_debug()
    log.setLevel( "WARNING" )

    for index in range( iterations_count ):
        log.debug( 'Message' )

def debug_tools_slowdebug_off(iterations_count):
    log = get_debug_tools()

    for index in range( iterations_count ):
        log( 2, 'Message' )

def debug_tools_fastdebug_off(iterations_count):
    log = get_debug_tools()
    log.setup( fast=True )

    for index in range( iterations_count ):
        log( 2, 'Message' )


def debug_tools_log_debug_on(iterations_count):
    log = get_debug_tools()
    log.setLevel( "DEBUG" )

    for index in range( iterations_count ):
        log.debug( 'Message' )

def logging_mod_log_debug_on(iterations_count):
    log = get_loggging_debug()
    log.setLevel( "DEBUG" )

    for index in range( iterations_count ):
        log.debug( 'Message' )

def debug_tools_slowdebug_on(iterations_count):
    log = get_debug_tools()

    for index in range( iterations_count ):
        log( 1, 'Message' )

def debug_tools_fastdebug_on(iterations_count):
    log = get_debug_tools()
    log.setup( fast=True )

    for index in range( iterations_count ):
        log( 1, 'Message' )


results= []
results.append( run_profiling( debug_tools_fastdebug_off, logging_mod_log_debug_off, 1, 10000000 ) )
results.append( run_profiling( debug_tools_slowdebug_off, logging_mod_log_debug_off, 1, 10000000 ) )
results.append( run_profiling( debug_tools_log_debug_off, logging_mod_log_debug_off, 1, 10000000 ) )

results.append( run_profiling( debug_tools_fastdebug_on, logging_mod_log_debug_on, 1, 100000 ) )
results.append( run_profiling( debug_tools_slowdebug_on, logging_mod_log_debug_on, 1, 100000 ) )
results.append( run_profiling( debug_tools_log_debug_on, logging_mod_log_debug_on, 1, 100000 ) )

print('\n\nResults details:')
for index, result in enumerate( results, start=1 ):
    print( "\n%2d. %s\n" % ( index, result[1] ) )

print('Results resume:')
for index, result in enumerate( results, start=1 ):
    print( '%2d. %10.5f %10.5f %10.5f  %s - %s  = %s iterations' % ( (index,) + result[0]) )
