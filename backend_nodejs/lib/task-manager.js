/**
 * Task Manager - Handle task analysis and chart generation
 */

const path = require('path');
const fs = require('fs');

// Try to load ChartJS, but don't fail if it's not available
let ChartJSNodeCanvas;
let canvasLib;
try {
  ChartJSNodeCanvas = require('chartjs-node-canvas').ChartJSNodeCanvas;
  canvasLib = require('canvas');
} catch (err) {
  console.warn('[TaskManager] ChartJS/Canvas not available, chart generation will be disabled');
  ChartJSNodeCanvas = null;
  canvasLib = null;
}

class TaskManager {
  constructor(db, staticDir) {
    this.db = db;
    this.staticDir = staticDir || path.join(__dirname, '..', 'db', 'static');
    
    // Ensure static directory exists
    if (!fs.existsSync(this.staticDir)) {
      fs.mkdirSync(this.staticDir, { recursive: true });
    }

    // Initialize ChartJS canvas only if available
    if (ChartJSNodeCanvas) {
      try {
        this.chartCanvas = new ChartJSNodeCanvas({
          width: 1400,
          height: 450,
          backgroundColour: 'white'
        });
      } catch (err) {
        console.warn('[TaskManager] Failed to initialize ChartJS:', err.message);
        this.chartCanvas = null;
      }
    } else {
      this.chartCanvas = null;
    }
  }

  /**
   * Decode task result from hex format (e.g., "0x02 0x01")
   * Returns { phase, result }
   */
  decodeResult(resultStr) {
    const TaskPhase = {
      UNKNOWN: 0,
      INITIATED: 1,
      PENDING: 2,
      REJECTED: 3,
      FINISHED: 4
    };

    const TaskResult = {
      UNKNOWN: 0,
      SUCCESS: 1,
      FAILED: 2
    };

    if (!resultStr || typeof resultStr !== 'string') {
      return { phase: 'UNKNOWN', result: 'UNKNOWN' };
    }

    const parts = resultStr.trim().split(/\s+/);
    if (parts.length !== 2) {
      return { phase: 'UNKNOWN', result: 'UNKNOWN' };
    }

    try {
      const phaseInt = parseInt(parts[0], 16);
      const resultInt = parseInt(parts[1], 16);

      const phaseNames = ['UNKNOWN', 'INITIATED', 'PENDING', 'REJECTED', 'FINISHED'];
      const resultNames = ['UNKNOWN', 'SUCCESS', 'FAILED'];

      return {
        phase: phaseNames[phaseInt] || 'UNKNOWN',
        result: resultNames[resultInt] || 'UNKNOWN'
      };
    } catch (err) {
      return { phase: 'UNKNOWN', result: 'UNKNOWN' };
    }
  }

  /**
   * Generate task summary statistics for a client
   */
  getTaskSummary(clientId) {
    const tasks = this.db.getAllTasks();
    
    const resultSummary = {
      total: 0,
      success: 0,
      failed: 0
    };

    const phaseSummary = {
      total: 0,
      initiate: 0,
      pending: 0,
      reject: 0,
      finish: 0
    };

    // Filter tasks by client_id if not "ALL"
    const filteredTasks = clientId === 'ALL' 
      ? tasks 
      : tasks.filter(t => t.client_id === clientId);

    filteredTasks.forEach(task => {
      resultSummary.total++;
      phaseSummary.total++;

      const { phase, result } = this.decodeResult(task.result || '0x00 0x00');

      // Count results
      if (result === 'SUCCESS') {
        resultSummary.success++;
      } else if (result === 'FAILED') {
        resultSummary.failed++;
      }

      // Count phases
      if (phase === 'INITIATED') {
        phaseSummary.initiate++;
      } else if (phase === 'PENDING') {
        phaseSummary.pending++;
      } else if (phase === 'REJECTED') {
        phaseSummary.reject++;
      } else if (phase === 'FINISHED') {
        phaseSummary.finish++;
      }
    });

    return { resultSummary, phaseSummary };
  }

  /**
   * Generate task summary chart and return as base64
   */
  async generateSummaryChart(clientId) {
    console.log(`[TaskManager] Starting chart generation for client: ${clientId}`);
    console.log(`[TaskManager] ChartCanvas available: ${!!this.chartCanvas}`);
    
    if (!this.chartCanvas) {
      console.warn('[TaskManager] Chart generation not available, returning text summary');
      // Return a simple text-based summary instead
      const { resultSummary, phaseSummary } = this.getTaskSummary(clientId);
      const summary = `Task Summary for ${clientId}:\n` +
        `Phases: Total=${phaseSummary.total}, Initiated=${phaseSummary.initiate}, Pending=${phaseSummary.pending}, Rejected=${phaseSummary.reject}, Finished=${phaseSummary.finish}\n` +
        `Results: Total=${resultSummary.total}, Success=${resultSummary.success}, Failed=${resultSummary.failed}`;
      console.log('[TaskManager] Text summary created:', summary);
      return Buffer.from(summary).toString('base64');
    }

    console.log('[TaskManager] Getting task summary data...');
    const { resultSummary, phaseSummary } = this.getTaskSummary(clientId);
    console.log('[TaskManager] Summary data:', { resultSummary, phaseSummary });

    try {
      // Create Phase Summary Chart
      const phaseConfig = {
        type: 'bar',
        data: {
          labels: ['Total', 'Initiated', 'Pending', 'Rejected', 'Finished'],
          datasets: [{
            label: 'Count',
            data: [
              phaseSummary.total,
              phaseSummary.initiate,
              phaseSummary.pending,
              phaseSummary.reject,
              phaseSummary.finish
            ],
            backgroundColor: ['#CBD5E0', '#667eea', '#4299e1', '#f56565', '#48bb78'],
            borderColor: '#e2e8f0',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: `Task Phase Summary - Client: ${clientId}`,
              font: { size: 18, weight: 'bold' }
            },
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { 
                stepSize: 1,
                font: { size: 14 }
              },
              title: {
                display: true,
                text: 'Count',
                font: { size: 16, weight: 'bold' }
              },
              grid: { display: true, drawBorder: true }
            },
            x: { 
              ticks: {
                font: { size: 14 }
              },
              grid: { display: false } 
            }
          }
        }
      };

      // Create Result Summary Chart
      const resultConfig = {
        type: 'bar',
        data: {
          labels: ['Total', 'Success', 'Failed'],
          datasets: [{
            label: 'Count',
            data: [resultSummary.total, resultSummary.success, resultSummary.failed],
            backgroundColor: ['#CBD5E0', '#48bb78', '#f56565'],
            borderColor: '#e2e8f0',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: `Task Result Summary - Client: ${clientId}`,
              font: { size: 18, weight: 'bold' }
            },
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { 
                stepSize: 1,
                font: { size: 14 }
              },
              title: {
                display: true,
                text: 'Count',
                font: { size: 16, weight: 'bold' }
              },
              grid: { display: true, drawBorder: true }
            },
            x: { 
              ticks: {
                font: { size: 14 }
              },
              grid: { display: false } 
            }
          }
        }
      };

      // Generate both charts
      console.log('[TaskManager] Generating phase chart...');
      const phaseBuffer = await this.chartCanvas.renderToBuffer(phaseConfig);
      console.log('[TaskManager] Generating result chart...');
      const resultBuffer = await this.chartCanvas.renderToBuffer(resultConfig);
      
      // Combine both images side by side using canvas
      const { createCanvas, loadImage } = canvasLib;
      
      const phaseImage = await loadImage(phaseBuffer);
      const resultImage = await loadImage(resultBuffer);
      
      // Create a combined canvas
      const combinedWidth = phaseImage.width + resultImage.width + 20; // 20px gap
      const combinedHeight = Math.max(phaseImage.height, resultImage.height);
      const combinedCanvas = createCanvas(combinedWidth, combinedHeight);
      const ctx = combinedCanvas.getContext('2d');
      
      // Fill background
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, combinedWidth, combinedHeight);
      
      // Draw both images
      ctx.drawImage(phaseImage, 0, 0);
      ctx.drawImage(resultImage, phaseImage.width + 20, 0);
      
      const imageBuffer = combinedCanvas.toBuffer('image/png');
      
      // Save to file
      const fileName = clientId === 'ALL' ? 'summary_all.png' : `summary_${clientId}.png`;
      const filePath = path.join(this.staticDir, fileName);
      fs.writeFileSync(filePath, imageBuffer);

      // Convert to base64
      const base64Image = imageBuffer.toString('base64');
      
      console.log(`[TaskManager] Generated chart for client ${clientId}, size: ${imageBuffer.length} bytes`);
      
      return base64Image;
    } catch (err) {
      console.error('[TaskManager] Error generating chart:', err);
      throw err;
    }
  }

  /**
   * Get task history for a specific client
   */
  getTaskHistory(clientId) {
    const tasks = this.db.getAllTasks();
    const filteredTasks = tasks.filter(t => t.client_id === clientId);

    return filteredTasks.map(task => {
      const { phase, result } = this.decodeResult(task.result || '0x00 0x00');
      return {
        task_id: task.task_id,
        phase: phase,
        result: result
      };
    });
  }
}

module.exports = TaskManager;
