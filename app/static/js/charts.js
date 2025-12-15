/**
 * Gestion des graphiques et historiques
 * Utilise Chart.js pour afficher les données de télémétrie
 */

let charts = {
  speed: null,
  distance: null,
  events: null,
  obstacles: null,
  stops: null,
  lightIntensity: null,
  speedHistogram: null,
  distanceHistogram: null,
  eventTypes: null
};

/**
 * Calcule le nombre d'heures basé sur la plage temporelle
 */
function getHoursFromRange(range) {
  switch(range) {
    case '1h': return 1;
    case '6h': return 6;
    case '24h': return 24;
    case '7d': return 168;
    default: return 24;
  }
}

/**
 * Charge les données historiques de télémétrie
 */
async function loadMetricsHistory(range) {
  try {
    const hours = getHoursFromRange(range);
    const response = await fetch(`/api/telemetry/stats?hours=${hours}`);
    if (!response.ok) {
      console.error('Erreur lors du chargement des statistiques');
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Erreur réseau:', error);
    return null;
  }
}

/**
 * Charge l'historique des événements
 */
async function loadEventsHistory(range) {
  try {
    const hours = getHoursFromRange(range);
    const response = await fetch(`/api/events/summary?hours=${hours}`);
    if (!response.ok) {
      console.error('Erreur lors du chargement des événements');
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Erreur réseau:', error);
    return null;
  }
}

/**
 * Crée un graphique de vitesse
 */
function createSpeedChart(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.speed) charts.speed.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour le graphique de vitesse');
    return;
  }
  
  // Inverser pour avoir l'ordre chronologique (du plus ancien au plus récent)
  const sortedData = [...data].reverse();
  
  const timestamps = sortedData.map(d => {
    const date = new Date(d.timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  });
  const speeds = sortedData.map(d => d.speed_pwm || 0);
  
  charts.speed = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timestamps,
      datasets: [{
        label: 'Vitesse (PWM)',
        data: speeds,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Vitesse du robot'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 255,
          title: {
            display: true,
            text: 'PWM (0-255)'
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
  console.log(`Graphique de vitesse créé avec ${speeds.length} points`);
}

/**
 * Crée un graphique de distance
 */
function createDistanceChart(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.distance) charts.distance.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour le graphique de distance');
    return;
  }
  
  // Inverser pour avoir l'ordre chronologique
  const sortedData = [...data].reverse();
  
  const timestamps = sortedData.map(d => {
    const date = new Date(d.timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  });
  const distances = sortedData.map(d => ((d.dist_traveled_cm || 0) / 100).toFixed(2));
  
  charts.distance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: timestamps,
      datasets: [{
        label: 'Distance parcourue (m)',
        data: distances,
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Distance parcourue'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Distance (m)'
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
  console.log(`Graphique de distance créé avec ${distances.length} points`);
}

/**
 * Crée un graphique des événements
 */
function createEventsChart(canvasId, events) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  if (charts.events) charts.events.destroy();
  
  // Compter les événements par type
  const eventCounts = {};
  events.events?.forEach(event => {
    eventCounts[event.event_type] = (eventCounts[event.event_type] || 0) + 1;
  });
  
  const labels = Object.keys(eventCounts);
  const counts = Object.values(eventCounts);
  
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#14b8a6'
  ];
  
  charts.events = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Nombre d\'événements',
        data: counts,
        backgroundColor: colors.slice(0, labels.length),
        borderColor: colors.slice(0, labels.length),
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Événements par type'
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Nombre'
          }
        }
      }
    }
  });
}

/**
 * Crée un graphique des obstacles
 */
function createObstaclesChart(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.obstacles) charts.obstacles.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour le graphique des obstacles');
    return;
  }
  
  // Inverser pour avoir l'ordre chronologique
  const sortedData = [...data].reverse();
  
  const timestamps = sortedData.map(d => {
    const date = new Date(d.timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  });
  const obstacles = sortedData.map(d => d.obstacle_events || 0);
  
  charts.obstacles = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: timestamps,
      datasets: [{
        label: 'Obstacles détectés',
        data: obstacles,
        backgroundColor: '#ef4444',
        borderColor: '#dc2626',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Obstacles détectés'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          title: {
            display: true,
            text: 'Nombre'
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
  console.log(`Graphique des obstacles créé avec ${obstacles.length} points`);
}

/**
 * Crée un graphique des arrêts (basé sur les événements)
 */
function createStopsChart(canvasId, events) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  if (charts.stops) charts.stops.destroy();
  
  // Compter les arrêts (emergency_stop events)
  let stopCount = 0;
  if (events.events) {
    events.events.forEach(event => {
      if (event.event_type && event.event_type.toLowerCase().includes('stop')) {
        stopCount++;
      }
    });
  }
  
  charts.stops = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Arrêts détectés'],
      datasets: [{
        data: [stopCount, Math.max(0, 10 - stopCount)],
        backgroundColor: ['#ef4444', '#e5e7eb'],
        borderColor: ['#dc2626', '#d1d5db'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `Nombre d'arrêts: ${stopCount}`
        }
      }
    }
  });
}

/**
 * Crée un graphique de l'intensité lumineuse
 */
function createLightIntensityChart(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.lightIntensity) charts.lightIntensity.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour le graphique d\'intensité lumineuse');
    return;
  }
  
  // Inverser pour avoir l'ordre chronologique
  const sortedData = [...data].reverse();
  
  const timestamps = sortedData.map(d => {
    const date = new Date(d.timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  });
  const lightLevels = sortedData.map(d => d.light_level || 0);
  
  charts.lightIntensity = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timestamps,
      datasets: [{
        label: 'Photorésistance',
        data: lightLevels,
        borderColor: '#eab308',
        backgroundColor: 'rgba(234, 179, 8, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#eab308',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Photorésistance'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Valeur'
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
  console.log(`Graphique d'intensité lumineuse créé avec ${lightLevels.length} points`);
}

/**
 * Crée un histogramme de vitesse
 */
function createSpeedHistogram(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.speedHistogram) charts.speedHistogram.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour l\'histogramme de vitesse');
    return;
  }
  
  // Regrouper les vitesses en plages
  const speedRanges = {
    'Arrêt (0%)': 0,
    'Lent (1-33%)': 0,
    'Moyen (34-66%)': 0,
    'Rapide (67-100%)': 0
  };
  
  data.forEach(d => {
    const avgSpeed = (d.speed_pwm || 0) / 255;
    if (avgSpeed === 0) speedRanges['Arrêt (0%)']++;
    else if (avgSpeed <= 0.33) speedRanges['Lent (1-33%)']++;
    else if (avgSpeed <= 0.66) speedRanges['Moyen (34-66%)']++;
    else speedRanges['Rapide (67-100%)']++;
  });
  
  charts.speedHistogram = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(speedRanges),
      datasets: [{
        label: 'Nombre de périodes',
        data: Object.values(speedRanges),
        backgroundColor: ['#94a3b8', '#60a5fa', '#34d399', '#fbbf24'],
        borderColor: ['#64748b', '#3b82f6', '#10b981', '#f59e0b'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Distribution des vitesses'
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Nombre'
          }
        }
      }
    }
  });
  console.log(`Histogramme de vitesse créé avec ${data.length} points`);
}

/**
 * Crée un histogramme de distance
 */
function createDistanceHistogram(canvasId, data) {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) {
    console.error(`Canvas ${canvasId} introuvable`);
    return;
  }
  
  if (charts.distanceHistogram) charts.distanceHistogram.destroy();
  
  if (!Array.isArray(data) || data.length === 0) {
    console.log('Aucune donnée pour l\'histogramme de distance');
    return;
  }
  
  // Regrouper les distances en plages
  const distanceRanges = {
    'Aucune (0m)': 0,
    'Courte (0-50m)': 0,
    'Moyenne (50-100m)': 0,
    'Longue (>100m)': 0
  };
  
  data.forEach(d => {
    const totalDist = (d.dist_traveled_cm || 0) / 100;
    if (totalDist === 0) distanceRanges['Aucune (0m)']++;
    else if (totalDist < 50) distanceRanges['Courte (0-50m)']++;
    else if (totalDist < 100) distanceRanges['Moyenne (50-100m)']++;
    else distanceRanges['Longue (>100m)']++;
  });
  
  charts.distanceHistogram = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(distanceRanges),
      datasets: [{
        label: 'Nombre de périodes',
        data: Object.values(distanceRanges),
        backgroundColor: ['#e5e7eb', '#86efac', '#4ade80', '#15803d'],
        borderColor: ['#d1d5db', '#65a30d', '#22c55e', '#166534'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Distribution des distances'
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Nombre'
          }
        }
      }
    }
  });
  console.log(`Histogramme de distance créé avec ${data.length} points`);
}

/**
 * Crée un graphique détaillé des types d'événements
 */
function createEventTypesChart(canvasId, events) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  if (charts.eventTypes) charts.eventTypes.destroy();
  
  // Compter les événements par type détaillé
  const eventCounts = {};
  if (events.events) {
    events.events.forEach(event => {
      const type = event.event_type || 'unknown';
      eventCounts[type] = (eventCounts[type] || 0) + 1;
    });
  }
  
  const labels = Object.keys(eventCounts);
  const counts = Object.values(eventCounts);
  
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#14b8a6', '#f97316', '#6366f1'
  ];
  
  charts.eventTypes = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: colors.slice(0, labels.length),
        borderColor: colors.slice(0, labels.length),
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'right',
          labels: {
            padding: 15,
            font: {
              size: 12
            }
          }
        },
        title: {
          display: true,
          text: 'Types d\'événements détaillés'
        }
      }
    }
  });
}

/**
 * Rafraîchit les graphiques détaillés
 */
async function refreshDetailedCharts(telemetryData = null) {
  const range = document.getElementById('timeRangeDetailed')?.value || '24h';
  const limit = getHoursFromRange(range) * 10;
  
  // Charger les données si non fournies
  if (!telemetryData) {
    const response = await fetch(`/api/telemetry/latest?limit=${limit}`);
    const result = await response.json();
    telemetryData = result.data || [];
  }
  
  // Créer les graphiques détaillés
  if (telemetryData && telemetryData.length > 0) {
    createSpeedHistogram('chartSpeedHistogram', telemetryData);
    createDistanceHistogram('chartDistanceHistogram', telemetryData);
    createLightIntensityChart('chartLightIntensity', telemetryData);
  }
  
  // Charger les événements
  const eventsData = await loadEventsHistory(range);
  if (eventsData) {
    createStopsChart('chartStops', eventsData);
    createEventTypesChart('chartEventTypes', eventsData);
  }
}

/**
 * Rafraîchit tous les graphiques
 */
async function refreshAllCharts() {
  console.log('=== RAFRAÎCHISSEMENT DES GRAPHIQUES ===');
  
  try {
    // Récupérer le nombre de points selon la plage temporelle
    const metricsRange = document.getElementById('timeRangeMetrics')?.value || '24h';
    const limit = getHoursFromRange(metricsRange) * 10; // ~10 points par heure
    
    // Charger les données de télémétrie brutes
    const response = await fetch(`/api/telemetry/latest?limit=${limit}`);
    const result = await response.json();
    const telemetryData = result.data || [];
    
    console.log(`Données de télémétrie chargées: ${telemetryData.length} points`);
    
    // Graphiques de métriques (vitesse et distance)
    if (telemetryData.length > 0) {
      createSpeedChart('chartSpeed', telemetryData);
      createDistanceChart('chartDistance', telemetryData);
      createObstaclesChart('chartObstacles', telemetryData);
    } else {
      console.warn('Aucune donnée de télémétrie disponible');
    }
    
    // Événements
    const eventsRange = document.getElementById('timeRangeEvents')?.value || '24h';
    const eventsData = await loadEventsHistory(eventsRange);
    if (eventsData) {
      createEventsChart('chartEvents', eventsData);
    }
    
    // Graphiques détaillés
    await refreshDetailedCharts(telemetryData);
    
    console.log('=== GRAPHIQUES RAFRAÎCHIS ===');
  } catch (error) {
    console.error('Erreur lors du rafraîchissement des graphiques:', error);
  }
}

/**
 * Initialise les écouteurs d'événements
 */
function initChartListeners() {
  // Boutons refresh
  document.getElementById('refreshMetricsBtn')?.addEventListener('click', refreshAllCharts);
  document.getElementById('refreshBatteryBtn')?.addEventListener('click', refreshAllCharts);
  document.getElementById('refreshEventsBtn')?.addEventListener('click', refreshAllCharts);
  document.getElementById('refreshDetailedBtn')?.addEventListener('click', refreshAllCharts);
  
  // Changements de plage temporelle
  document.getElementById('timeRangeMetrics')?.addEventListener('change', refreshAllCharts);
  document.getElementById('timeRangeBattery')?.addEventListener('change', refreshAllCharts);
  document.getElementById('timeRangeEvents')?.addEventListener('change', refreshAllCharts);
  document.getElementById('timeRanEventsBtn')?.addEventListener('click', refreshAllCharts);
  document.getElementById('refreshDetailedBtn')?.addEventListener('click', refreshAllCharts);
}

// Initialiser les graphiques au chargement de la page
window.addEventListener('load', () => {
  console.log("=== INITIALISATION DES GRAPHIQUES ===");
  initChartListeners();
  refreshAllCharts();
  
  // Rafraîchir périodiquement les graphiques toutes les 5 minutes
  setInterval(() => {
    refreshAllCharts();
  }, 300000);
});
