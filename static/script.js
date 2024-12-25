let simulationData = null;
let currentStep = 0;
let animationInterval = null;
let processCounter = 1;

function addProcess() {
    const processList = document.getElementById('process-list');
     const processItem = document.createElement('div');
      processItem.className = 'process-item';
      processItem.innerHTML = `
          <span>Process ${processCounter}</span>
          <div class="input-group">
              <label>Burst Time:</label>
              <input type="number" class="burst-time" min="1" value="1" id="burst_time_${processCounter}">
           </div>
           <div class="input-group">
              <label>Arrival Time:</label>
             <input type="number" class="arrival-time" min="0" value="0" id="arrival_time_${processCounter}">
          </div>
           <div class="input-group">
               <label>Priority:</label>
               <input type="number" class="priority" min="1" value="1" id="priority_${processCounter}">
          </div>
         <button onclick="this.parentElement.remove()">Remove</button>
     `;
      processList.appendChild(processItem);
    processCounter++;
}

 async function startSimulation() {
    const schedulingType = document.getElementById('schedulingType').value;
    const formData = new FormData();
    formData.append('schedulingType', schedulingType);
   formData.append('processCount', processCounter-1);
  
   for (let i = 1; i < processCounter; i++) {
      const burstTime = document.getElementById(`burst_time_${i}`).value;
      const arrivalTime = document.getElementById(`arrival_time_${i}`).value;
      const priority = document.getElementById(`priority_${i}`).value;

      formData.append(`burst_time_${i}`, burstTime);
      formData.append(`arrival_time_${i}`, arrivalTime);
      formData.append(`priority_${i}`, priority);
   }
   
    const response = await fetch('/simulate', {
        method: 'POST',
        body: formData
    });
    simulationData = await response.json();
    currentStep = 0;
    
    // Clear any existing animation
    if (animationInterval) {
        clearInterval(animationInterval);
    }
    
    // Start animation
    animationInterval = setInterval(updateVisualization, 1000);
}

function updateVisualization() {
    if (!simulationData || currentStep >= simulationData.history.length) {
        clearInterval(animationInterval);
        displayStatistics();
        return;
    }
     const step = simulationData.history[currentStep];
     document.getElementById('time-indicator').textContent = `Time: ${step.time}`;
    
    // Update SVG
    const svg = document.querySelector('#visualization svg');
    
    // Clear previous processes
    const processes = svg.querySelectorAll('.process');
    processes.forEach(p => p.remove());
    
    // Draw running process
    if (step.running) {
        const runningProcess = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        runningProcess.setAttribute("cx", "400");
        runningProcess.setAttribute("cy", "200");
        runningProcess.setAttribute("r", "20");
        runningProcess.setAttribute("fill", step.running.color);
        runningProcess.setAttribute("class", "process");
        svg.appendChild(runningProcess);
        
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "400");
        text.setAttribute("y", "200");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("fill", "white");
        text.textContent = `P${step.running.pid}`;
        svg.appendChild(text);
    }
    
    // Draw queue
    step.queue.forEach((process, index) => {
        const queueProcess = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        queueProcess.setAttribute("cx", String(100 + index * 50));
        queueProcess.setAttribute("cy", "200");
        queueProcess.setAttribute("r", "20");
        queueProcess.setAttribute("fill", process.color);
        queueProcess.setAttribute("class", "process");
        svg.appendChild(queueProcess);
        
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", String(100 + index * 50));
        text.setAttribute("y", "200");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("fill", "white");
        text.textContent = `P${process.pid}`;
        svg.appendChild(text);
    });
    
    updateTimeline();
    currentStep++;
}

function updateTimeline() {
    const svg = document.querySelector('#timeline svg');
    svg.innerHTML = '';
    
    // Draw timeline
    const timelineY = 100;
    const timelineStart = 50;
    const timelineWidth = 700;
    
    // Base timeline
    const timeline = document.createElementNS("http://www.w3.org/2000/svg", "line");
    timeline.setAttribute("x1", String(timelineStart));
    timeline.setAttribute("y1", String(timelineY));
    timeline.setAttribute("x2", String(timelineStart + timelineWidth));
    timeline.setAttribute("y2", String(timelineY));
    timeline.setAttribute("stroke", "black");
    svg.appendChild(timeline);
    
    // Draw process executions
    const timeUnit = timelineWidth / simulationData.history.length;
    for (let i = 0; i <= currentStep; i++) {
        const step = simulationData.history[i];
        if (step.running) {
            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", String(timelineStart + i * timeUnit));
            rect.setAttribute("y", String(timelineY - 20));
            rect.setAttribute("width", String(timeUnit));
            rect.setAttribute("height", "40");
            rect.setAttribute("fill", step.running.color);
            svg.appendChild(rect);
            
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", String(timelineStart + i * timeUnit + timeUnit/2));
            text.setAttribute("y", String(timelineY));
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("dominant-baseline", "middle");
            text.setAttribute("fill", "white");
            text.textContent = `P${step.running.pid}`;
            svg.appendChild(text);
        }
    }
}

 function displayStatistics() {
    const stats = simulationData.statistics;
    const statsDiv = document.getElementById('statistics');
    let tableHTML = `
        <h2>Statistics</h2>
         <p>Average Waiting Time: ${stats.average_waiting_time}</p>
         <p>Average Turnaround Time: ${stats.average_turnaround_time}</p>
         <p>Average Response Time: ${stats.average_response_time}</p>
         <p>Completion Order: ${stats.completion_order.map(pid => 'P'+pid).join(' → ')}</p>
        <table>
            <thead>
                <tr>
                    <th>Process ID</th>
                     <th>Priority</th>
                    <th>Waiting Time</th>
                    <th>Turnaround Time</th>
                     <th>Completion Time</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    stats.process_details.forEach(process => {
      tableHTML += `
            <tr>
                <td>P${process.pid}</td>
                <td>${process.priority}</td>
                <td>${process.waiting_time}</td>
                <td>${process.turnaround_time}</td>
                 <td>${process.completion_time}</td>
            </tr>
       `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    statsDiv.innerHTML = tableHTML;
  }