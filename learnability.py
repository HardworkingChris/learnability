#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lif import *
from syn import *
from da_stdp import *

def setup_network(params):
    #prefs.codegen.target = 'weave'
    set_device('cpp_standalone')
    defaultclock.dt = 1.0*ms
    neurons = LifNeurons(1000, params)
    excitatory_synapses = DaStdpSynapses(neurons, params)
    ConnectSparse(excitatory_synapses, 'i < 800 and ' + params['condition'],
                  params['connectivity'], params['w_exc'], params['post_delay'])
    inhibitory_synapses = InhibitorySynapses(neurons, params)
    ConnectSparse(inhibitory_synapses, 'i >= 800 and ' + params['condition'],
                  params['connectivity'], params['w_inh'], params['post_delay'])
    network = Network()
    network.add(neurons, excitatory_synapses, inhibitory_synapses)
    return neurons, excitatory_synapses, inhibitory_synapses, network

def run_sim(name, index, duration, neurons, excitatory_synapses, network, params):
    print("Simulation Started: {0} {1}".format(name, index))
    rate_monitor = PopulationRateMonitor(neurons)
    spike_monitor = SpikeMonitor(neurons)
    #state_monitor = StateMonitor(excitatory_synapses, 'w', record=range(params['neurons']*params['syn_per_neuron']))
    network.add(rate_monitor, spike_monitor)#, state_monitor)
    network.run(duration, report='stdout', report_period=60*second)
    device.build(directory='output', compile=True, run=True, debug=False)
    #periods = int(duration / 60*second)
    #spikes = ndarray((0, 2))
    #from timeit import default_timer
    #real_start_time = default_timer()
    #weights = ndarray((periods + 1, size(excitatory_synapses.w)))
    #weights[0] = excitatory_synapses.w
    #for period in range(1, periods + 1):
    #    spike_monitor = SpikeMonitor(neurons)
    #    network.add(spike_monitor)
    #    network.run(1*second)
    #    device.build(directory='output', compile=True, run=True, debug=False)
    #    spikes = append(spikes, array((spike_monitor.t, spike_monitor.i)).T, axis=0)
    #    network.remove(spike_monitor)
    #    network.run(59*second)
    #    device.build(directory='output', compile=True, run=True, debug=False)
    #    real_elapsed_time = default_timer() - real_start_time
    #    print("Simulation Status: {0} {1} - {2:%} in {3} sec.".format(
    #          name, index, float(period) / periods, real_elapsed_time))
    #    weights[period] = excitatory_synapses.w
    filename = "{0}_{1}".format(name, index)
    numpy.savez_compressed(filename, duration=duration, params=params,
                           t=rate_monitor.t, rate=rate_monitor.rate,
                           syn=array((excitatory_synapses.i, excitatory_synapses.j, excitatory_synapses.w)),
                           spk=array((spike_monitor.t, spike_monitor.i)))
    print("Simulation Ended: {0} {1}".format(name, index))

class Unpacker(object):
    def __init__(self, fn):
        self.fn = fn
    def __call__(self, packed):
        print "unpacked: {0}".format(packed)
        self.fn(*packed)

def run_parallel(fn, inputs):
    unpacker = Unpacker(fn)
    from multiprocessing import Pool
    pool = Pool()
    pool.map(unpacker, inputs)
    pool.close()
    pool.join()
