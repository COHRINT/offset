#!/usr/bin/env python

__author__ = "Ian Loefgren"
__date__ = "1.4.2019"

"""
Implements framework for handling simple message passing in a distributed
event-triggered filtering scenario.

Usage:
"""

import numpy as np
from numpy.linalg import inv
from copy import deepcopy
# import pudb; pudb.set_trace()
import time

from .covar_intersect import covar_intersect, gen_sim_transform
from .helpers.msg_handling import MeasurementMsg, StateMsg

class Agent(object):
    
    def __init__(self,agent_id,connections,meas_connections,neighbor_connections,
                    local_filter,common_estimates,x_true,msg_drop_prob,tau_goal,
                    tau,use_adaptive_tau):    
        # agent id
        self.agent_id = agent_id
        
        # ids of connections
        self.connections = tuple(connections)
        self.meas_connections = tuple(meas_connections)
        self.neighbor_connections = tuple(neighbor_connections)
        
        # number of states per platform
        self.num_states = 4
        
        # filter selfect for local estimation
        self.local_filter = local_filter
        
        # struct with ids of connections and filters estimating common
        self.common_estimates = common_estimates
        
        # true starting position and MSE
        self.true_state = [x_true]
        self.mse_history = []
        
        # CI trigger count
        self.ci_trigger_cnt = 0
        self.ci_trigger_rate = 0
        
        self.msgs_sent = 0
        self.total_msgs = 0
        
        self.msg_success_prob = 1-msg_drop_prob
        
        # CI thresholding data
        self.tau_goal = tau_goal
        self.tau = tau
        self.connection_tau_rates = np.zeros( (len(self.connections),1) )
        self.epsilon_1 = 0.05
        self.epsilon_2 = 0.1

        self.use_adaptive_tau = use_adaptive_tau

        self.ci_process_worst_case_time = 0

    def get_location(self,id_):
        """
        Get location of agent specified by :param id in state estimate, as well as indicies.

        :param id - scalar id

        TODO:
        - add support for list of ids
        """
        loc = []
        idx = []

        # create list of agents in state estimate, incl. self
        ids = list(self.connections)
        ids.append(self.agent_id)
        ordered_ids = sorted(ids)

        # find location of id in state estimate ids, as well as indices
        loc = ordered_ids.index(id_)
        idx = list(range(self.num_states*loc,self.num_states*loc+self.num_states))

        return loc, idx

    def get_id(self,loc):
        """ 
        Get id of agent from location in state estimate
        
        :param loc -> int - location in state estimate
        """
        ids = list(self.connections)
        ids.append(self.agent_id)
        ordered_ids = sorted(ids)
        return ordered_ids[loc]

    def process_local_measurements(self,input_,local_measurements):
        """
        Handle control input and locally collected measurements.
        Propagates local and common information filters, and handles measurement
        messages.

        :param input -> np.array - control input vector
        :param local_measurements -> list of msgs - lisr of meas. msgs

        TODO: compare iterating w/ randperm vs w/o - does it actually matter?
        """
        
        # get self location and index
        agent_loc,agent_idx = self.get_location(self.agent_id)

        # create correctly-sized input vector to apply from local control input
        input_vec = np.zeros( (self.local_filter.G.shape[1],1) )
        input_vec[2*agent_loc:2*agent_loc+2] = np.reshape(input_,(input_.shape[0],1))

        # propagate local and common info filters
        self.local_filter.predict(input_vec)
        for filter_ in self.common_estimates:
            # common information filters get no knowledge of control input
            # b/c others have no idea what your control input was
            filter_.predict(np.zeros( (filter_.G.shape[1],1) ))

        # create outgoing and 'loopback' message queues
        outgoing = []
        loopback = []

        # process each collected measurement
        for msg in local_measurements:
            
            # unpack msg
            src = msg.src
            dest = msg.dest
            target = msg.target
            status = msg.status
            type_ = msg.type_
            data = msg.data

            # make sure source of measurement is current agent
            assert(src == self.agent_id)

            # update local filter
            self.local_filter.msg_update(msg)

            # threshold measurement and update w/ relevant common info ests
            for id_ in self.meas_connections:

                # update msg destination to be measurement connection
                dest = id_

                # regenerate message
                msg = MeasurementMsg(src,dest,target,status,type_,data)

                # find common estimate associated w/ msg destination
                for filter_ in self.common_estimates:
                    
                    # if filter estimates destination agent 
                    if filter_.meas_connection is msg.dest:

                        # threshold measurement
                        src_,dest_,target_,status_,type_,data_ = filter_.threshold(msg)

                        # TODO: update to call w/ list of ids, not individual
                        idx = deepcopy(agent_idx)
                        for conn_id in filter_.connection:
                            loc,idx1 = self.get_location(conn_id)
                            idx += idx1
                        # get unique ids by converting to set object
                        idx = set(idx)
                        # convert back to list and sort
                        idx = list(idx)
                        idx.sort()

                        # generate new message
                        msg = MeasurementMsg(src_,dest_,target_,status_,type_,data_)

                        # increment msg sent counts
                        self.msgs_sent += sum(status_)
                        self.total_msgs += len(status_)

                        # add msg to update filter to loopback queue and outgoing
                        # (this is so as to not affect thresholding w/ updates)
                        x_local = self.local_filter.x[idx]

                        # extract submatrix
                        idxgrid = np.ix_(idx,idx) # creates correct row and column references
                        P_local = self.local_filter.P[idxgrid]

                        outgoing.append(msg)
                        loopback.append([msg,x_local,P_local])

        # process measurements in loopback queue
        for msg in loopback:

            msg_ = msg[0]
            x_local = msg[1]
            P_local = msg[2]

            for filter_ in self.common_estimates:

                # find estimate associated w/ msg destination
                if filter_.meas_connection == msg_.dest:

                    # update filter
                    filter_.msg_update(msg_,x_local,P_local)

        return outgoing

    def process_received_measurements(self,inbox):
        """
        Update local and common information filters w/ inbox msg queue.

        :param inbox -> list - list of recevied messages
        """

        # get self location and index
        agent_loc,agent_idx = self.get_location(self.agent_id)

        for msg in inbox:

            # make sure message dest is current agent
            assert(msg.dest == self.agent_id)

            # imperfect comms sim: coin flip for dropping message
            # TODO: add binomial draw w/ msgs drop prob here
             
            # update local filter
            x_local = self.local_filter.x
            P_local = self.local_filter.P
            self.local_filter.msg_update(msg,x_local,P_local)

            # update common information filters
            for filter_ in self.common_estimates:

                # TODO: update to call w/ list of ids, not individual
                idx = deepcopy(agent_idx)
                for conn_id in filter_.connection:
                    loc,idx1 = self.get_location(conn_id)
                    idx += idx1
                # get unique ids by converting to set object
                idx = set(idx)
                # convert back to list and sort
                idx = list(idx)
                idx.sort()

                x_local_comm = self.local_filter.x[idx]

                # extract submatrix
                idxgrid = np.ix_(idx,idx) # creates correct row and column references
                P_local_comm = self.local_filter.P[idxgrid]

                # find common estimate associated w/ msg source
                if filter_.meas_connection == msg.src:
                    filter_.msg_update(msg,x_local_comm,P_local_comm)

    def gen_ci_message(self,dest_id,dest_connections):
        """
        Generates messages to be sent to connections to perform CI.

        Inputs:

            dest_id             -- agent id of message destination
            dest_connections    -- ids of connections to agent who is receiving message

        Outputs:

            msg -- CI message of type StateMsg
        """

        xa = deepcopy(self.local_filter.x)
        Pa = deepcopy(self.local_filter.P)

        # construct transform
        Ta, il_a, inter = gen_sim_transform(self.agent_id,list(self.connections),
                                            dest_id,dest_connections)

        # compute reduced, transformed state estimate
        xaT = np.dot(inv(Ta),xa)
        xaTred = xaT[0:il_a]
        PaT = np.dot(inv(Ta),np.dot(Pa,Ta))
        PaTred_grid = np.ix_(np.arange(0,il_a),np.arange(0,il_a))
        PaTred = PaT[PaTred_grid]

        msg = StateMsg(self.agent_id,
                        dest_id,
                        self.meas_connections,
                        self.connections,
                        xaTred,
                        PaTred,
                        self.ci_trigger_rate)

        return msg

    def process_ci_messages(self,msgs):
        """
        Process received covariance intersection message, and perform factorized
        covariance update on local and common information estimates.

        Inputs:

            msg -- covariance intersection message of type StateMsg

        Returns:

            none
        """

        for msg in msgs:
            
            start_time = time.clock()

            # grab state estimate from local filter
            xa = deepcopy(self.local_filter.x)
            Pa = deepcopy(self.local_filter.P)

            # unpack estimate from message
            xb = msg.state_est
            Pb = msg.est_cov
            b_id = msg.src
            b_connections = msg.src_connections
            b_rate = msg.src_ci_rate

            # construct transform
            Ta, il_a, inter = gen_sim_transform(self.agent_id,list(self.connections),
                                                b_id,list(b_connections))

            # compute reduced, transformed state estimate
            xaT = np.dot(inv(Ta),xa)
            xaTred = xaT[0:il_a]
            PaT = np.dot(inv(Ta),np.dot(Pa,Ta))
            PaTred_grid = np.ix_(np.arange(0,il_a),np.arange(0,il_a))
            PaTred = PaT[PaTred_grid]

            # reduced estimate from sender is already reduced
            xbTred = xb
            PbTred = Pb

            # perform covariance intersection with reduced estimates
            alpha = np.ones((PaTred.shape[0],1))
            xc, Pc = covar_intersect(xaTred,xbTred,PaTred,PbTred,alpha)

            # compute information delta for conditional update
            invD = inv(Pc) - inv(PaTred)
            invDd = np.dot(inv(Pc),xc) - np.dot(inv(PaTred),xaTred)

            # conditional gaussian update
            if (PaT.shape[0]-Pc.shape[0] == 0) or (PaT.shape[1]-Pc.shape[1] == 0):
                cond_cov = invD
                cond_mean = invDd
            else:
                cond_cov_row1 = np.hstack( (invD,np.zeros((Pc.shape[0],PaT.shape[1]-Pc.shape[1]))) )
                cond_cov_row2 = np.hstack( (np.zeros((PaT.shape[0]-Pc.shape[0],Pc.shape[1])),np.zeros((PaT.shape[0]-Pc.shape[0],PaT.shape[0]-Pc.shape[0]))) )
                cond_cov = np.vstack( (cond_cov_row1,cond_cov_row2) )
                cond_mean = np.vstack( (invDd,np.zeros((PaT.shape[0]-Pc.shape[0],1))) )
            
            V = inv(inv(PaT) + cond_cov)
            v = np.dot(V,np.dot(inv(PaT),xaT) + cond_mean)

            # transform back to normal state order
            xa = np.dot(Ta,v)
            Pa = np.dot(Ta,np.dot(V,inv(Ta)))

            # update local estimates
            self.local_filter.x = deepcopy(xa)
            self.local_filter.P = deepcopy(Pa)

            # update common estimates
            for i, filter_ in enumerate(self.common_estimates):
                if filter_.meas_connection == b_id:
                    filter_.x = deepcopy(xc)
                    filter_.P = deepcopy(Pc)
                    self.connection_tau_rates[i] = b_rate

            # update CI threshold w/ adaptive thresholding heuristic
            if self.use_adaptive_tau:
                self.tau = min(self.tau_goal,self.tau + 
                                self.epsilon_1*sum(-self.connection_tau_rates +
                                self.ci_trigger_rate) +
                                self.epsilon_2*(self.tau_goal-self.tau))

            time_elapsed = time.clock() - start_time
            if time_elapsed > self.ci_process_worst_case_time: self.ci_process_worst_case_time = time_elapsed

def test_agent():
    pass

if __name__ == "__main__":
    test_agent()