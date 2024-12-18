import heapq
import plotly.graph_objects as go
from tabulate import tabulate
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation


def priority_preemptive_scheduling(processes):
    """
    Implements Priority (Preemptive) Scheduling without a Process class.

    Args:
        processes: A list of dictionaries, each representing a process.

    Returns:
        A tuple:
            - a list of finished processes (dictionaries).
            - the total completion time.
    """

    current_time = 0
    finished_processes = []
    priority_queue = []  # Heapq for priority

    process_index = 0  # keeps track of current process in original list

    # Print initial table
    initial_table = [[p["priority"], f"P{p['pid']}", p["arrival_time"]] for p in processes]
    print("\nInitial Process Table:")
    print(tabulate(initial_table, headers=["Priority", "PID", "Arrival Time"], tablefmt="grid"))

    execution_log = []  # For detailed table
    
    # Adding additional fields
    for process in processes:
       process["remaining_time"] = process["burst_time"]
       process["start_time"] = -1
       process["completion_time"] = -1
       process["turnaround_time"] = -1
       process["waiting_time"] = -1
       process["remaining_history"] = [process["burst_time"]]


    previous_process = None # keeps track of current process
    while process_index < len(processes) or priority_queue:
        # 1. add newly arrived processes
        while (
            process_index < len(processes)
            and processes[process_index]["arrival_time"] <= current_time
        ):
            heapq.heappush(priority_queue, (processes[process_index]["priority"], processes[process_index]["arrival_time"],process_index))
            process_index += 1

        # 2. if queue is empty, move to next available process arrival time
        if not priority_queue:
            if process_index < len(processes):
                current_time = processes[process_index]["arrival_time"]
            else:
                break
            continue

        # 3. process the highest priority process (that has arrived)
        priority , arrival, index = heapq.heappop(priority_queue)
        current_process = processes[index]

        # set start time if it hasn't started yet
        if current_process["start_time"] == -1:
            current_process["start_time"] = current_time

        # when the process changes update the remaining history
        if previous_process != current_process and previous_process is not None:
          previous_process["remaining_history"].append(previous_process["remaining_time"])

        current_process["remaining_time"] -= 1
        
        current_time += 1  # increase time by 1 unit
        execution_log.append((current_time, current_process))
        
        # 4. if the process finished, calculate completion time, turn around time, and wait time
        if current_process["remaining_time"] == 0:
            current_process["completion_time"] = current_time
            current_process["turnaround_time"] = current_process["completion_time"] - current_process["arrival_time"]
            current_process["waiting_time"] = current_process["turnaround_time"] - current_process["burst_time"]
            finished_processes.append(current_process)
            # after completion update history
            current_process["remaining_history"].append(current_process["remaining_time"])
        # 5. if the process is not finished, put it back to the queue
        else:
            heapq.heappush(priority_queue, (current_process["priority"], current_process["arrival_time"], index))
        
        previous_process = current_process

    total_completion_time = current_time

    # Print detailed table
    detailed_table_data = []
    for process in processes:
        remaining_str = " / ".join(map(str, process["remaining_history"]))
        detailed_table_data.append([
            f"P{process['pid']}",
            process["priority"],
            process["arrival_time"],
            process["completion_time"],
            process["turnaround_time"],
            process["waiting_time"],
            remaining_str
        ])
    print("\nProcess Execution Details:")
    print(
        tabulate(
            detailed_table_data,
            headers=[
                "PID",
                "Priority",
                "Arrival Time",
                "CT",
                "Turnaround Time",
                "Waiting Time",
                "Remaining Time History"
            ],
            tablefmt="grid",
        )
    )

    return finished_processes, total_completion_time, execution_log



def create_gantt_chart(execution_log, total_completion_time):
    """Creates a Gantt chart using Plotly."""

    tasks = []
    previous_time = 0
    previous_process = None

    for time, process in execution_log:
      if previous_process != process and previous_process is not None:
         tasks.append({
            'Task': f'P{previous_process['pid']}',
            'Start': previous_time,
            'Finish': time
         })
         previous_time = time
      previous_process = process
    if previous_process is not None:
      tasks.append({
        'Task': f'P{previous_process['pid']}',
        'Start': previous_time,
        'Finish': total_completion_time
      })
        
    
    fig = go.Figure([go.Bar(
        y=[task['Task'] for task in tasks],
        x=[task['Finish']-task['Start'] for task in tasks],
        base=[task['Start'] for task in tasks],
        orientation='h'
    )])
    
    fig.update_layout(
        title="Gantt Chart for Priority Preemptive Scheduling",
        xaxis_title="Time",
        yaxis_title="Processes",
        xaxis=dict(range=[0, total_completion_time]),
        bargap=0.3
    )

    fig.show()


def create_animation(processes, execution_log, total_completion_time):
  """Creates a Matplotlib animation to visualize the scheduling."""

  fig, ax = plt.subplots(figsize=(12, 6))
  ax.set_xlim(0, total_completion_time)
  ax.set_ylim(0, len(processes) + 2)
  ax.set_xlabel("Time")
  ax.set_ylabel("Processes / Queue")
  ax.set_title("Priority Preemptive Scheduling Animation")
  ax.set_yticks(range(0, len(processes) + 2))
  ax.set_yticklabels(['Queue'] + [f'P{p["pid"]}' for p in processes] + [''])
  
  process_rects = {
     p["pid"]: None for p in processes
  }
  
  
  queue_items = []

  def update(frame):
    """Updates the animation frame."""
    ax.clear()
    ax.set_xlim(0, total_completion_time)
    ax.set_ylim(0, len(processes) + 2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Processes / Queue")
    ax.set_title("Priority Preemptive Scheduling Animation")
    ax.set_yticks(range(0, len(processes) + 2))
    ax.set_yticklabels(['Queue'] + [f'P{p["pid"]}' for p in processes] + [''])

    queue_items = []

    for time, process in execution_log[:frame+1]:
      
      for queue_item in process_rects:
        rect = process_rects[queue_item]
        if rect and rect.get_y() != 0:
          rect.set_facecolor('lightgray') # make inactive processes light gray

      # when process starts create a box
      if process["start_time"] == time -1:
          y = [i for i, p in enumerate(processes) if p["pid"] == process["pid"]][0] + 1
          rect = patches.Rectangle(
              (time - 1, y - 0.4),
              1,
             0.8,
              facecolor='skyblue',
              edgecolor='black'
          )
          process_rects[process["pid"]] = rect
          ax.add_patch(rect)


      # update current process
      if process["start_time"] <= time -1:
            
          y = [i for i, p in enumerate(processes) if p["pid"] == process["pid"]][0] + 1
          rect = process_rects[process["pid"]]
          if rect:
             rect.set_width(time - rect.get_x() if time > rect.get_x() else 1)
             rect.set_facecolor('skyblue')
             ax.add_patch(rect)
           


    for i in range(len(processes)):
        proc = processes[i]
        if proc["arrival_time"] <= frame:
            if proc["completion_time"] == -1 or proc["completion_time"] > frame:
              queue_items.append(f"P{proc['pid']}")
    
    
    queue_text = ", ".join(queue_items)
    ax.text(0.5,0.5, f"Queue: {queue_text}", horizontalalignment='center', verticalalignment='center')

    return ax,

  ani = FuncAnimation(fig, update, frames = total_completion_time , repeat=False, blit=False)
  plt.show()

if __name__ == "__main__":
    processes = [
        {"pid":1, "arrival_time":0, "burst_time":10, "priority":3},
        {"pid":2, "arrival_time":0, "burst_time":1, "priority":1},
        {"pid":3, "arrival_time":0, "burst_time":2, "priority":4},
        {"pid":4, "arrival_time":0, "burst_time":1, "priority":5},
        {"pid":5, "arrival_time":0, "burst_time":5, "priority":2},
    ]

    finished_processes, total_completion_time, execution_log = priority_preemptive_scheduling(processes)

    print("\nPriority (Preemptive) Scheduling:")
    print("---------------------------------")
    print("Finished Processes (by completion order):")
    for process in finished_processes:
      print(f"Process P{process['pid']}: Completion Time = {process['completion_time']}, Turnaround Time = {process['turnaround_time']}, Waiting Time = {process['waiting_time']}")

    print(f"\nTotal Completion Time: {total_completion_time}")

    total_turnaround_time = sum([p["turnaround_time"] for p in finished_processes])
    avg_turnaround_time = total_turnaround_time / len(finished_processes)

    total_waiting_time = sum([p["waiting_time"] for p in finished_processes])
    avg_waiting_time = total_waiting_time / len(finished_processes)

    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")
    print(f"Average Waiting Time: {avg_waiting_time:.2f}")
    
    create_gantt_chart(execution_log, total_completion_time)
    create_animation(processes, execution_log, total_completion_time)