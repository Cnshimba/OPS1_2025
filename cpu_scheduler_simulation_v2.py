import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

# Define Process type: (pid, arrival, burst, priority)
Process = Tuple[str, int, int, int]

# Scheduling Functions
def fcfs_scheduling(processes: List[Process]) -> List[Tuple[str, int, int]]:
    """First-Come-First-Serve Scheduling: Non-preemptive."""
    processes = sorted(processes, key=lambda x: x[1])
    current_time = 0
    schedule = []
    for pid, arrival, burst, _ in processes:
        start_time = max(current_time, arrival)
        end_time = start_time + burst
        schedule.append((pid, start_time, end_time))
        current_time = end_time
    return schedule

def sjn_scheduling(processes: List[Process]) -> List[Tuple[str, int, int]]:
    """Shortest Job Next Scheduling: Non-preemptive."""
    processes = processes.copy()
    current_time = 0
    schedule = []
    ready_queue = []
    while processes or ready_queue:
        while processes and processes[0][1] <= current_time:
            ready_queue.append(processes.pop(0))
        if ready_queue:
            ready_queue.sort(key=lambda x: x[2])
            pid, arrival, burst, _ = ready_queue.pop(0)
            start_time = current_time
            end_time = start_time + burst
            schedule.append((pid, start_time, end_time))
            current_time = end_time
        else:
            current_time = processes[0][1] if processes else current_time + 1
    return schedule

def sjn_preemptive_scheduling(processes: List[Process]) -> List[Tuple[str, int, int]]:
    """Shortest Job Next with Preemption (SRTF): Preemptive."""
    processes = [(pid, arrival, burst, burst, priority) for pid, arrival, burst, priority in processes]
    current_time = min(p[1] for p in processes)
    schedule = []
    ready_queue = []
    active_process = None
    while processes or ready_queue or active_process:
        while processes and processes[0][1] <= current_time:
            ready_queue.append(processes.pop(0))
        if not active_process and ready_queue:
            ready_queue.sort(key=lambda x: x[2])
            active_process = ready_queue.pop(0)
        if active_process:
            pid, arrival, remaining, original_burst, priority = active_process
            start_time = current_time
            next_arrival = min((p[1] for p in processes if p[1] > current_time), default=float('inf'))
            time_slice = min(1, remaining, max(1, next_arrival - current_time))
            current_time += time_slice
            remaining -= time_slice
            schedule.append((pid, start_time, current_time))
            new_arrivals = [p for p in processes if p[1] <= current_time]
            if new_arrivals:
                ready_queue.extend(new_arrivals)
                processes = [p for p in processes if p[1] > current_time]
                ready_queue.sort(key=lambda x: x[2])
                if ready_queue and ready_queue[0][2] < remaining:
                    ready_queue.append((pid, arrival, remaining, original_burst, priority))
                    active_process = ready_queue.pop(0)
                elif remaining == 0:
                    active_process = None
                else:
                    active_process = (pid, arrival, remaining, original_burst, priority)
            elif remaining == 0:
                active_process = None
            else:
                active_process = (pid, arrival, remaining, original_burst, priority)
        else:
            current_time += 1
    return schedule

def round_robin_scheduling(processes: List[Process], quantum: int) -> List[Tuple[str, int, int]]:
    """Round Robin Scheduling: Preemptive."""
    queue = [(pid, arrival, burst, priority) for pid, arrival, burst, priority in processes]
    current_time = 0
    schedule = []
    while queue:
        pid, arrival, burst, priority = queue.pop(0)
        start_time = max(current_time, arrival)
        time_slice = min(quantum, burst)
        end_time = start_time + time_slice
        schedule.append((pid, start_time, end_time))
        current_time = end_time
        remaining_burst = burst - time_slice
        if remaining_burst > 0:
            queue.append((pid, arrival, remaining_burst, priority))
    return schedule

def priority_scheduling(processes: List[Process]) -> List[Tuple[str, int, int]]:
    """Priority Scheduling: Non-preemptive."""
    processes = sorted(processes, key=lambda x: (x[3], x[1]))
    current_time = 0
    schedule = []
    for pid, arrival, burst, priority in processes:
        start_time = max(current_time, arrival)
        end_time = start_time + burst
        schedule.append((pid, start_time, end_time))
        current_time = end_time
    return schedule

def priority_preemptive_scheduling(processes: List[Process]) -> List[Tuple[str, int, int]]:
    """Priority Scheduling with Preemption: Preemptive."""
    processes = [(pid, arrival, burst, burst, priority) for pid, arrival, burst, priority in processes]
    current_time = min(p[1] for p in processes)
    schedule = []
    ready_queue = []
    active_process = None
    while processes or ready_queue or active_process:
        while processes and processes[0][1] <= current_time:
            ready_queue.append(processes.pop(0))
        if not active_process and ready_queue:
            ready_queue.sort(key=lambda x: x[4])
            active_process = ready_queue.pop(0)
        if active_process:
            pid, arrival, remaining, original_burst, priority = active_process
            start_time = current_time
            next_arrival = min((p[1] for p in processes if p[1] > current_time), default=float('inf'))
            time_slice = min(1, remaining, max(1, next_arrival - current_time))
            current_time += time_slice
            remaining -= time_slice
            schedule.append((pid, start_time, current_time))
            new_arrivals = [p for p in processes if p[1] <= current_time]
            if new_arrivals:
                ready_queue.extend(new_arrivals)
                processes = [p for p in processes if p[1] > current_time]
                ready_queue.sort(key=lambda x: x[4])
                if ready_queue and ready_queue[0][4] < priority:
                    ready_queue.append((pid, arrival, remaining, original_burst, priority))
                    active_process = ready_queue.pop(0)
                elif remaining == 0:
                    active_process = None
                else:
                    active_process = (pid, arrival, remaining, original_burst, priority)
            elif remaining == 0:
                active_process = None
            else:
                active_process = (pid, arrival, remaining, original_burst, priority)
        else:
            current_time += 1
    return schedule

# Waiting Time Calculation Functions
def calculate_waiting_time(schedule: List[Tuple[str, int, int]], processes: List[Process]) -> Tuple[dict, float, dict, float, dict, float]:
    """Calculate metrics for non-preemptive algorithms."""
    process_dict = {p[0]: p[1] for p in processes}
    first_starts = {}
    completion_times = {}
    for pid, start, end in schedule:
        if pid not in first_starts:
            first_starts[pid] = start
        completion_times[pid] = end
    waiting_times = {pid: max(0, first_starts[pid] - process_dict[pid]) for pid in process_dict if pid in first_starts}
    turnaround_times = {pid: completion_times[pid] - process_dict[pid] for pid in process_dict}
    response_times = {pid: first_starts[pid] - process_dict[pid] for pid in process_dict}
    avg_waiting = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
    avg_turnaround = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0
    avg_response = sum(response_times.values()) / len(response_times) if response_times else 0
    return waiting_times, avg_waiting, turnaround_times, avg_turnaround, response_times, avg_response

def calculate_preemptive_waiting_time(schedule: List[Tuple[str, int, int]], processes: List[Process]) -> Tuple[dict, float, dict, float, dict, float]:
    """Calculate metrics for preemptive algorithms."""
    process_dict = {p[0]: (p[1], p[2]) for p in processes}
    waiting_times = {}
    first_starts = {}
    completion_times = {}
    last_end = {}
    for pid, start, end in schedule:
        if pid not in first_starts:
            first_starts[pid] = start
        if pid in process_dict:
            arrival, _ = process_dict[pid]
            if pid not in waiting_times:
                waiting_times[pid] = max(0, start - arrival)
            elif pid in last_end:
                waiting_times[pid] += start - last_end[pid]
            last_end[pid] = end
        completion_times[pid] = end
    turnaround_times = {pid: completion_times[pid] - process_dict[pid][0] for pid in process_dict}
    response_times = {pid: first_starts[pid] - process_dict[pid][0] for pid in process_dict}
    avg_waiting = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
    avg_turnaround = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0
    avg_response = sum(response_times.values()) / len(response_times) if response_times else 0
    return waiting_times, avg_waiting, turnaround_times, avg_turnaround, response_times, avg_response

# Streamlit UI
def main():
    st.title("Process Scheduling Simulator v2")
    st.sidebar.header("Process Configuration")
    
    num_processes = st.sidebar.number_input("Number of Processes", min_value=1, max_value=10, value=3)
    quantum = st.sidebar.number_input("Time Quantum (for Round Robin)", min_value=1, value=2)
    
    # Process input
    process_list = []
    for i in range(num_processes):
        with st.sidebar.expander(f"Process P{i+1}"):
            arrival = st.number_input(f"Arrival Time P{i+1}", min_value=0, value=i, key=f"arr_{i}")
            burst = st.number_input(f"Burst Time P{i+1}", min_value=1, value=24 if i == 0 else 3, key=f"burst_{i}")
            priority = st.number_input(f"Priority P{i+1}", min_value=1, value=1, key=f"prio_{i}")
        process_list.append((f"P{i+1}", arrival, burst, priority))
    
    # Load Example
    st.sidebar.header("Load Example")
    example = st.sidebar.selectbox("Select Example", ["None", "Test Case 1: Long First Process"])
    if example == "Test Case 1: Long First Process" and st.sidebar.button("Load"):
        process_list = [("P1", 0, 24, 1), ("P2", 1, 3, 1), ("P3", 2, 3, 1)]
        st.sidebar.write("Loaded: P1 (0, 24, 1), P2 (1, 3, 1), P3 (2, 3, 1)")
        st.session_state.process_list = process_list
    
    if "process_list" in st.session_state:
        process_list = st.session_state.process_list
    
    algorithm_options = ["FCFS", "SJN", "SJN with Preemption", "Round Robin", "Priority", "Priority with Preemption"]
    algorithm = st.selectbox("Select Scheduling Algorithm", algorithm_options)
    
    def run_simulation(processes, algo, quantum):
        if algo == "FCFS":
            schedule = fcfs_scheduling(processes)
            wt, awt, tt, att, rt, art = calculate_waiting_time(schedule, processes)
        elif algo == "SJN":
            schedule = sjn_scheduling(processes)
            wt, awt, tt, att, rt, art = calculate_waiting_time(schedule, processes)
        elif algo == "SJN with Preemption":
            schedule = sjn_preemptive_scheduling(processes)
            wt, awt, tt, att, rt, art = calculate_preemptive_waiting_time(schedule, processes)
        elif algo == "Round Robin":
            schedule = round_robin_scheduling(processes, quantum)
            wt, awt, tt, att, rt, art = calculate_preemptive_waiting_time(schedule, processes)
        elif algo == "Priority":
            schedule = priority_scheduling(processes)
            wt, awt, tt, att, rt, art = calculate_waiting_time(schedule, processes)
        elif algo == "Priority with Preemption":
            schedule = priority_preemptive_scheduling(processes)
            wt, awt, tt, att, rt, art = calculate_preemptive_waiting_time(schedule, processes)
        
        total_time = schedule[-1][2] - min(p[1] for p in processes)
        busy_time = sum(p[2] for p in processes)
        cpu_util = (busy_time / total_time) * 100 if total_time > 0 else 0
        throughput = len(processes) / total_time if total_time > 0 else 0
        
        return schedule, wt, awt, tt, att, rt, art, cpu_util, throughput
    
    if st.button("Run Simulation"):
        try:
            schedule, waiting_times, avg_waiting, turnaround_times, avg_turnaround, response_times, avg_response, cpu_utilization, throughput = run_simulation(process_list, algorithm, quantum)
            
            # Display Schedule
            df = pd.DataFrame(schedule, columns=["Process", "Start Time", "End Time"])
            st.subheader("Execution Schedule")
            st.table(df)
            
            # Display Metrics
            st.subheader("Performance Metrics")
            st.write(f"**Average Waiting Time:** {avg_waiting:.2f} units")
            st.write(f"**Average Turnaround Time:** {avg_turnaround:.2f} units")
            st.write(f"**Average Response Time:** {avg_response:.2f} units")
            st.write(f"**CPU Utilization:** {cpu_utilization:.2f}%")
            st.write(f"**Throughput:** {throughput:.2f} processes/unit time")
            st.write("Per Process Metrics:", {pid: f"Wait={waiting_times[pid]:.2f}, Turn={turnaround_times[pid]:.2f}, Resp={response_times[pid]:.2f}" for pid in waiting_times})
            
            # Gantt Chart
            fig, ax = plt.subplots(figsize=(10, 2))
            colors = plt.cm.Paired(np.linspace(0, 1, len(schedule)))
            for i, (pid, start, end) in enumerate(schedule):
                ax.barh(0, end - start, left=start, height=0.5, color=colors[i], edgecolor='black')
                ax.text(start + (end - start) / 2, 0, pid, ha='center', va='center', color='black', fontweight='bold')
            ax.set_yticks([])
            ax.set_xticks([s[1] for s in schedule] + [schedule[-1][2]])
            ax.set_xlabel("Time")
            ax.set_title(f"{algorithm} Gantt Chart")
            plt.tight_layout()
            st.pyplot(fig)
            
            # Export Results
            csv = df.to_csv(index=False) + f"\nAvg Waiting Time,{avg_waiting:.2f}\nAvg Turnaround Time,{avg_turnaround:.2f}\nAvg Response Time,{avg_response:.2f}\nCPU Utilization,{cpu_utilization:.2f}\nThroughput,{throughput:.2f}"
            st.download_button("Download Results", csv, f"{algorithm}_results.csv", "text/csv")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    if st.button("Compare All"):
        try:
            results = {}
            for algo in algorithm_options:
                schedule, wt, awt, tt, att, rt, art, cpu_util, throughput = run_simulation(process_list, algo, quantum)
                results[algo] = {
                    "Avg Wait": f"{awt:.2f}",
                    "Avg Turnaround": f"{att:.2f}",
                    "Avg Response": f"{art:.2f}",
                    "CPU Util (%)": f"{cpu_util:.2f}",
                    "Throughput": f"{throughput:.2f}"
                }
            st.subheader("Comparison of All Algorithms")
            st.table(pd.DataFrame(results))
        
        except Exception as e:
            st.error(f"An error occurred during comparison: {str(e)}")

if __name__ == "__main__":
    main()