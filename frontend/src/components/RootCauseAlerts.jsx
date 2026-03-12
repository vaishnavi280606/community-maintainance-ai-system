import { Paper, Typography, Box, Chip } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

export default function RootCauseAlerts({ rootCauses = [] }) {
  if (rootCauses.length === 0) {
    return (
      <Paper sx={{ p: 3, height: '100%', borderRadius: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Root Cause Alerts</Typography>
        <Typography variant="body2" color="text.secondary">No systemic issues detected</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, maxHeight: 420, overflow: 'auto', borderRadius: 4 }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>Root Cause Alerts</Typography>
      {rootCauses.map((rc, i) => (
        <Box key={i} sx={{
          p: 2, mb: 1.5, borderRadius: 3,
          bgcolor: rc.severity === 'Critical' ? 'rgba(198,40,40,0.06)' : 'rgba(230,81,0,0.06)',
          border: '1px solid',
          borderColor: rc.severity === 'Critical' ? 'rgba(198,40,40,0.2)' : 'rgba(230,81,0,0.2)',
          transition: 'transform 0.15s ease',
          '&:hover': { transform: 'translateX(4px)' },
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <WarningIcon fontSize="small" sx={{
              color: rc.severity === 'Critical' ? '#c62828' : '#e65100',
            }} />
            <Typography variant="body2" fontWeight={700}>{rc.issue}</Typography>
            <Chip label={rc.severity} size="small" sx={{
              fontWeight: 700, height: 22,
              bgcolor: rc.severity === 'Critical' ? 'rgba(198,40,40,0.1)' : 'rgba(230,81,0,0.1)',
              color: rc.severity === 'Critical' ? '#c62828' : '#e65100',
            }} />
          </Box>
          <Typography variant="caption" display="block" color="text.secondary" sx={{ mb: 0.5 }}>
            {rc.evidence}
          </Typography>
          <Typography variant="caption" display="block">
            <b>Root Cause:</b> {rc.root_cause_hypothesis}
          </Typography>
          {rc.recommendations && (
            <Box sx={{ mt: 0.5 }}>
              <Typography variant="caption" fontWeight={700}>Recommendations:</Typography>
              {rc.recommendations.map((r, j) => (
                <Typography key={j} variant="caption" display="block" sx={{ pl: 1 }}>
                  &bull; {r}
                </Typography>
              ))}
            </Box>
          )}
        </Box>
      ))}
    </Paper>
  );
}
