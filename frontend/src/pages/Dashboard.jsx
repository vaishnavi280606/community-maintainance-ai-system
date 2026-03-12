import { useState, useEffect } from 'react';
import {
  Box, Grid, Paper, Typography, CircularProgress
} from '@mui/material';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale,
  LinearScale, BarElement, PointElement, LineElement, Filler } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import { getDashboardStats, getRSI, getMaintenancePredictions, getRootCause } from '../api';
import { useAuth } from '../AuthContext';
import KPICards from '../components/KPICards';
import RootCauseAlerts from '../components/RootCauseAlerts';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [rsi, setRsi] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [rootCauses, setRootCauses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsRes, rsiRes, predRes, rcRes] = await Promise.all([
          getDashboardStats(),
          getRSI().catch(() => ({ data: [] })),
          getMaintenancePredictions().catch(() => ({ data: [] })),
          getRootCause().catch(() => ({ data: [] })),
        ]);
        setStats(statsRes.data);
        setRsi(rsiRes.data);
        setPredictions(predRes.data);
        setRootCauses(rcRes.data);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <CircularProgress size={48} sx={{ color: '#1a237e' }} />
    </Box>
  );

  if (!stats) return <Typography>No data available</Typography>;

  const categoryData = {
    labels: Object.keys(stats.category_distribution || {}),
    datasets: [{
      data: Object.values(stats.category_distribution || {}),
      backgroundColor: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140'],
      borderWidth: 0,
    }],
  };

  const priorityData = {
    labels: Object.keys(stats.priority_distribution || {}),
    datasets: [{
      label: 'Complaints by Priority',
      data: Object.values(stats.priority_distribution || {}),
      backgroundColor: ['rgba(67,233,123,0.8)', 'rgba(79,172,254,0.8)', 'rgba(250,112,154,0.8)', 'rgba(102,126,234,0.8)'],
      borderRadius: 8,
      borderSkipped: false,
    }],
  };

  const statusData = {
    labels: Object.keys(stats.status_distribution || {}),
    datasets: [{
      label: 'Complaints by Status',
      data: Object.values(stats.status_distribution || {}),
      backgroundColor: ['rgba(79,172,254,0.8)', 'rgba(250,112,154,0.8)', 'rgba(102,126,234,0.8)', 'rgba(67,233,123,0.8)', 'rgba(158,158,158,0.8)'],
      borderRadius: 8,
      borderSkipped: false,
    }],
  };

  const trendData = {
    labels: (stats.monthly_trend || []).map(t => t.month),
    datasets: [{
      label: 'Monthly Complaints',
      data: (stats.monthly_trend || []).map(t => t.count),
      borderColor: '#667eea',
      backgroundColor: 'rgba(102,126,234,0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#667eea',
      pointBorderWidth: 0,
      pointRadius: 5,
    }],
  };

  const chartOptions = {
    maintainAspectRatio: false,
    responsive: true,
    plugins: { legend: { labels: { font: { family: 'Inter', weight: 600 }, padding: 16 } } },
  };

  const barOptions = {
    ...chartOptions,
    scales: {
      y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { family: 'Inter' } } },
      x: { grid: { display: false }, ticks: { font: { family: 'Inter' } } },
    },
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          {user?.role === 'admin' ? 'Admin Dashboard' :
           user?.role === 'technician' ? 'My Tasks' : 'My Dashboard'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Overview of your community maintenance system
        </Typography>
      </Box>

      {/* KPI Cards */}
      <KPICards stats={stats} />

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, height: 340, borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Category Distribution</Typography>
            <Box sx={{ height: 270 }}>
              <Pie data={categoryData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, height: 340, borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Priority Distribution</Typography>
            <Box sx={{ height: 270 }}>
              <Bar data={priorityData} options={barOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, height: 340, borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Status Overview</Typography>
            <Box sx={{ height: 270 }}>
              <Bar data={statusData} options={barOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Trend + RSI */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 3, height: 340, borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Complaint Trend</Typography>
            <Box sx={{ height: 270 }}>
              <Line data={trendData} options={{
                ...barOptions,
                scales: {
                  ...barOptions.scales,
                  y: { ...barOptions.scales.y, grid: { color: 'rgba(0,0,0,0.04)' } },
                },
              }} />
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3, height: 340, overflow: 'auto', borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>RSI Heatmap</Typography>
            {rsi.length === 0 ? (
              <Typography variant="body2" color="text.secondary">No RSI data available</Typography>
            ) : (
              rsi.map((item, i) => (
                <Box key={i} sx={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  p: 1.5, mb: 1, borderRadius: 2.5,
                  bgcolor: item.color + '12', borderLeft: `4px solid ${item.color}`,
                  transition: 'transform 0.15s ease',
                  '&:hover': { transform: 'translateX(4px)' },
                }}>
                  <Typography variant="body2" fontWeight={600}>{item.location}</Typography>
                  <Typography variant="body2" fontWeight={800} color={item.color}>
                    {item.score}/100
                  </Typography>
                </Box>
              ))
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Predictions + Root Cause */}
      {user?.role === 'admin' && (
        <Grid container spacing={3} sx={{ mt: 1, mb: 2 }}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 3, maxHeight: 420, overflow: 'auto', borderRadius: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>
                Maintenance Predictions
              </Typography>
              {predictions.length === 0 ? (
                <Typography variant="body2" color="text.secondary">No predictions available</Typography>
              ) : (
                predictions.map((p, i) => (
                  <Box key={i} sx={{
                    p: 2, mb: 1.5, borderRadius: 3,
                    bgcolor: p.risk_level === 'High' ? 'rgba(250,112,154,0.08)' :
                             p.risk_level === 'Medium' ? 'rgba(79,172,254,0.08)' : 'rgba(67,233,123,0.08)',
                    border: '1px solid',
                    borderColor: p.risk_level === 'High' ? 'rgba(250,112,154,0.3)' :
                                 p.risk_level === 'Medium' ? 'rgba(79,172,254,0.3)' : 'rgba(67,233,123,0.3)',
                    transition: 'transform 0.15s ease',
                    '&:hover': { transform: 'translateX(4px)' },
                  }}>
                    <Typography variant="body2" fontWeight={700}>{p.asset_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Next failure: {p.predicted_next_failure} | Risk: {p.risk_level}
                    </Typography>
                    <br />
                    <Typography variant="caption" color="text.secondary">
                      Preventive by: {p.suggested_preventive_date}
                    </Typography>
                  </Box>
                ))
              )}
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <RootCauseAlerts rootCauses={rootCauses} />
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
