let processes = [];

// Step 1: Create dynamic process input fields
function createProcessInputs() {
  const num = parseInt(document.getElementById("numProcesses").value);
  const container = document.getElementById("processInputs");
  container.innerHTML = "";
  processes = [];

  if (isNaN(num) || num <= 0) {
    alert("Enter a valid number of processes");
    return;
  }

  for (let i = 0; i < num; i++) {
    const div = document.createElement("div");
    div.className = "input-box";
    div.innerHTML = `
      <h3>Process ${i + 1}</h3>
      <label>Process ID:</label>
      <input type="text" id="pid${i}" placeholder="P${i + 1}" required>
      <label>Arrival Time:</label>
      <input type="number" id="arrival${i}" placeholder="0" required>
      <label>Burst Time:</label>
      <input type="number" id="burst${i}" placeholder="5" required>
      <label>Priority:</label>
      <input type="number" id="priority${i}" placeholder="1" required>
    `;
    container.appendChild(div);
  }
}

// Step 2: Collect process data
function getProcessData() {
  processes = [];
  const num = parseInt(document.getElementById("numProcesses").value);
  for (let i = 0; i < num; i++) {
    const pid = document.getElementById(`pid${i}`).value;
    const arrival = parseInt(document.getElementById(`arrival${i}`).value);
    const burst = parseInt(document.getElementById(`burst${i}`).value);
    const priority = parseInt(document.getElementById(`priority${i}`).value);
    if (!pid || isNaN(arrival) || isNaN(burst) || isNaN(priority)) {
      alert("Fill all process fields correctly");
      return false;
    }
    processes.push({ pid, arrival, burst, priority, remaining: burst });
  }
  return true;
}

// Step 3: Main simulate function
function simulate() {
  if (!getProcessData()) return;

  const algo = document.getElementById("algorithm").value;
  const timeQuantum = parseInt(document.getElementById("timeQuantum").value) || 2;

  let result = []; // Gantt chart data
  let completedProcesses = [];

  // Sort by arrival time initially
  processes.sort((a, b) => a.arrival - b.arrival);

  if (algo === "FCFS") {
    let time = 0;
    processes.forEach(p => {
      if (time < p.arrival) time = p.arrival;
      p.start = time;
      p.completion = time + p.burst;
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      time += p.burst;
      result.push({ pid: p.pid, start: p.start, end: p.completion });
      completedProcesses.push(p);
    });
  } else if (algo === "SJF") {
    let time = 0;
    let remaining = [...processes];
    while (remaining.length > 0) {
      let available = remaining.filter(p => p.arrival <= time);
      if (available.length === 0) {
        time++;
        continue;
      }
      available.sort((a, b) => a.burst - b.burst);
      let p = available[0];
      p.start = time;
      p.completion = time + p.burst;
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      time += p.burst;
      result.push({ pid: p.pid, start: p.start, end: p.completion });
      completedProcesses.push(p);
      remaining = remaining.filter(x => x.pid !== p.pid);
    }
  } else if (algo === "SRTF") {
    let time = 0;
    let remaining = [...processes];
    let gantt = [];
    while (remaining.some(p => p.remaining > 0)) {
      let available = remaining.filter(p => p.arrival <= time && p.remaining > 0);
      if (available.length === 0) {
        time++;
        continue;
      }
      available.sort((a, b) => a.remaining - b.remaining);
      let p = available[0];
      p.remaining -= 1;
      gantt.push({ pid: p.pid, time: time });
      time++;
    }
    // Merge gantt times into blocks
    let merged = [];
    let current = gantt[0];
    for (let i = 1; i < gantt.length; i++) {
      if (gantt[i].pid === current.pid) {
        continue;
      } else {
        merged.push({ pid: current.pid, start: current.time - (current.pid.length), end: gantt[i].time });
        current = gantt[i];
      }
    }
    // For simplicity, just show PIDs in Gantt chart
    result = gantt.map(g => ({ pid: g.pid, start: g.time, end: g.time + 1 }));
    // Calculate CT, TAT, WT
    processes.forEach(p => {
      let times = result.filter(r => r.pid === p.pid);
      p.completion = Math.max(...times.map(r => r.end));
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      completedProcesses.push(p);
    });
  } else if (algo === "PRIORITY_NP") {
    let time = 0;
    let remaining = [...processes];
    while (remaining.length > 0) {
      let available = remaining.filter(p => p.arrival <= time);
      if (available.length === 0) { time++; continue; }
      available.sort((a, b) => a.priority - b.priority);
      let p = available[0];
      p.start = time;
      p.completion = time + p.burst;
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      time += p.burst;
      result.push({ pid: p.pid, start: p.start, end: p.completion });
      completedProcesses.push(p);
      remaining = remaining.filter(x => x.pid !== p.pid);
    }
  } else if (algo === "PRIORITY_P") {
    let time = 0;
    let remaining = [...processes];
    while (remaining.some(p => p.remaining > 0)) {
      let available = remaining.filter(p => p.arrival <= time && p.remaining > 0);
      if (available.length === 0) { time++; continue; }
      available.sort((a, b) => a.priority - b.priority);
      let p = available[0];
      p.remaining -= 1;
      result.push({ pid: p.pid, start: time, end: time + 1 });
      time++;
    }
    processes.forEach(p => {
      let times = result.filter(r => r.pid === p.pid);
      p.completion = Math.max(...times.map(r => r.end));
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      completedProcesses.push(p);
    });
  } else if (algo === "RR") {
    let time = 0;
    let remaining = [...processes];
    let queue = [];
    remaining.forEach(p => queue.push(p));
    while (queue.length > 0) {
      let p = queue.shift();
      if (p.remaining > timeQuantum) {
        if (time < p.arrival) time = p.arrival;
        result.push({ pid: p.pid, start: time, end: time + timeQuantum });
        time += timeQuantum;
        p.remaining -= timeQuantum;
        // add back to queue if remaining
        queue.push(p);
      } else {
        if (time < p.arrival) time = p.arrival;
        result.push({ pid: p.pid, start: time, end: time + p.remaining });
        time += p.remaining;
        p.remaining = 0;
      }
    }
    processes.forEach(p => {
      let times = result.filter(r => r.pid === p.pid);
      p.completion = Math.max(...times.map(r => r.end));
      p.turnaround = p.completion - p.arrival;
      p.waiting = p.turnaround - p.burst;
      completedProcesses.push(p);
    });
  }

  updateTable(completedProcesses);
  drawGantt(result);
}

// Step 4: Update table
function updateTable(list) {
  const tbody = document.getElementById("processTable");
  tbody.innerHTML = "";
  let totalWT = 0, totalTAT = 0;
  list.forEach(p => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${p.pid}</td><td>${p.arrival}</td><td>${p.burst}</td><td>${p.priority}</td><td>${p.completion}</td><td>${p.turnaround}</td><td>${p.waiting}</td>`;
    tbody.appendChild(row);
    totalWT += p.waiting;
    totalTAT += p.turnaround;
  });
  const avg = document.getElementById("averages");
  avg.innerHTML = `<h3>Average Waiting Time: ${(totalWT / list.length).toFixed(2)} | Average Turnaround Time: ${(totalTAT / list.length).toFixed(2)}</h3>`;
}

// Step 5: Draw Gantt Chart
function drawGantt(list) {
  const gantt = document.getElementById("ganttChart");
  gantt.innerHTML = "";
  list.forEach(p => {
    const block = document.createElement("div");
    block.className = "gantt-block";
    block.style.width = (p.end - p.start) * 30 + "px"; // width proportional to time
    block.innerText = p.pid;
    gantt.appendChild(block);
  });
}    