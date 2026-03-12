import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  ReportProblem as OpenIcon,
  Assignment as AssignedIcon,
  CheckCircle as ResolvedIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

const cards = (stats) => [
  {
    title: 'Total Complaints',
    value: stats.total_complaints,
    icon: <OpenIcon sx={{ fontSize: 28 }} />,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    shadow: 'rgba(102,126,234,0.4)',
  },
  {
    title: 'Open',
    value: stats.open_complaints,
    icon: <OpenIcon sx={{ fontSize: 28 }} />,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    shadow: 'rgba(245,87,108,0.4)',
  },
  {
    title: 'Resolved',
    value: stats.resolved_complaints,
    icon: <ResolvedIcon sx={{ fontSize: 28 }} />,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    shadow: 'rgba(79,172,254,0.4)',
  },
  {
    title: 'Avg Resolution (hrs)',
    value: stats.avg_resolution_time_hours || 'N/A',
    icon: <SpeedIcon sx={{ fontSize: 28 }} />,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    shadow: 'rgba(67,233,123,0.4)',
  },
];

export default function KPICards({ stats }) {
  if (!stats) return null;

  return (
    <Grid container spacing={3}>
      {cards(stats).map((card, idx) => (
        <Grid key={idx} size={{ xs: 12, sm: 6, md: 3 }}>
          <Paper sx={{
            p: 2.5, display: 'flex', alignItems: 'center', gap: 2,
            borderRadius: 4, border: 'none', position: 'relative', overflow: 'hidden',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 12px 28px ${card.shadow}` },
          }}>
            {/* Decorative blob */}
            <Box sx={{
              position: 'absolute', right: -20, top: -20, width: 80, height: 80,
              borderRadius: '50%', background: card.gradient, opacity: 0.08,
            }} />
            <Box sx={{
              background: card.gradient, borderRadius: 3, p: 1.5,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', boxShadow: `0 4px 14px ${card.shadow}`,
              minWidth: 50, minHeight: 50,
            }}>
              {card.icon}
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary" fontWeight={500}>{card.title}</Typography>
              <Typography variant="h4" fontWeight={800}>{card.value}</Typography>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
}
