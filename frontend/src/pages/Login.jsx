import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, TextField, Button, Typography,
  ToggleButtonGroup, ToggleButton, Alert, CircularProgress,
  Accordion, AccordionSummary, AccordionDetails, Chip,
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { login, register } from '../api';
import { useAuth } from '../AuthContext';

const DEMO_ACCOUNTS = [
  { role: 'Admin', username: 'admin', password: 'admin123', color: '#ff1744' },
  { role: 'Resident', username: 'resident1', password: 'resident123', color: '#00bfa5' },
  { role: 'Technician', username: 'tech_electrical', password: 'tech123', color: '#ff9100', spec: 'Electrical' },
  { role: 'Technician', username: 'tech_plumbing', password: 'tech123', color: '#ff9100', spec: 'Plumbing' },
  { role: 'Technician', username: 'tech_elevator', password: 'tech123', color: '#ff9100', spec: 'Elevator' },
  { role: 'Technician', username: 'tech_general', password: 'tech123', color: '#ff9100', spec: 'General' },
];

export default function Login() {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({
    username: '', password: '', email: '',
    first_name: '', last_name: '', role: 'resident',
    block: '', flat_number: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      let res;
      if (mode === 'login') {
        res = await login({ username: form.username, password: form.password });
      } else {
        res = await register(form);
      }
      loginUser(res.data.user, res.data.tokens);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || JSON.stringify(err.response?.data) || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0d1642 0%, #1a237e 30%, #283593 60%, #00695c 100%)',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Decorative circles */}
      <Box sx={{
        position: 'absolute', width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(0,191,165,0.15) 0%, transparent 70%)',
        top: -100, right: -100,
      }} />
      <Box sx={{
        position: 'absolute', width: 300, height: 300, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(26,35,126,0.3) 0%, transparent 70%)',
        bottom: -80, left: -80,
      }} />

      <Card sx={{
        width: 460, p: 1, borderRadius: 4,
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)',
      }}>
        <CardContent sx={{ p: 4 }}>
          {/* Logo */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{
              width: 60, height: 60, borderRadius: 3, mx: 'auto', mb: 1.5,
              background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 8px 24px rgba(26,35,126,0.3)',
            }}>
              <Typography variant="h4" fontWeight={900} sx={{ color: '#fff' }}>C</Typography>
            </Box>
            <Typography variant="h5" fontWeight={800} sx={{
              background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              CMS AI
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Community Maintenance System
            </Typography>
          </Box>

          <ToggleButtonGroup
            value={mode}
            exclusive
            onChange={(_, v) => v && setMode(v)}
            fullWidth
            sx={{
              mb: 3, borderRadius: 2, overflow: 'hidden',
              '& .MuiToggleButton-root': {
                fontWeight: 700, textTransform: 'none', py: 1,
                border: 'none', color: '#666',
                '&.Mui-selected': {
                  background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                  color: '#fff',
                  '&:hover': { bgcolor: '#283593' },
                },
              },
            }}
          >
            <ToggleButton value="login">Sign In</ToggleButton>
            <ToggleButton value="register">Sign Up</ToggleButton>
          </ToggleButtonGroup>

          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            <TextField label="Username" name="username" value={form.username}
              onChange={handleChange} fullWidth required sx={{ mb: 2 }} size="small"
              InputProps={{ sx: { borderRadius: 2 } }} />
            <TextField label="Password" name="password" type="password" value={form.password}
              onChange={handleChange} fullWidth required sx={{ mb: 2 }} size="small"
              InputProps={{ sx: { borderRadius: 2 } }} />

            {mode === 'register' && (
              <>
                <TextField label="Email" name="email" type="email" value={form.email}
                  onChange={handleChange} fullWidth required sx={{ mb: 2 }} size="small"
                  InputProps={{ sx: { borderRadius: 2 } }} />
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField label="First Name" name="first_name" value={form.first_name}
                    onChange={handleChange} fullWidth size="small"
                    InputProps={{ sx: { borderRadius: 2 } }} />
                  <TextField label="Last Name" name="last_name" value={form.last_name}
                    onChange={handleChange} fullWidth size="small"
                    InputProps={{ sx: { borderRadius: 2 } }} />
                </Box>
                <ToggleButtonGroup
                  value={form.role}
                  exclusive
                  onChange={(_, v) => v && setForm({ ...form, role: v })}
                  fullWidth
                  sx={{
                    mb: 2, borderRadius: 2, overflow: 'hidden',
                    '& .MuiToggleButton-root': {
                      fontWeight: 600, textTransform: 'none', fontSize: 13,
                      border: '1px solid #e0e0e0', color: '#666',
                      '&.Mui-selected': {
                        bgcolor: '#e8eaf6', color: '#1a237e', borderColor: '#1a237e',
                        '&:hover': { bgcolor: '#c5cae9' },
                      },
                    },
                  }}
                  size="small"
                >
                  <ToggleButton value="resident">Resident</ToggleButton>
                  <ToggleButton value="admin">Admin</ToggleButton>
                  <ToggleButton value="technician">Technician</ToggleButton>
                </ToggleButtonGroup>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField label="Block" name="block" value={form.block}
                    onChange={handleChange} fullWidth size="small"
                    InputProps={{ sx: { borderRadius: 2 } }} />
                  <TextField label="Flat No." name="flat_number" value={form.flat_number}
                    onChange={handleChange} fullWidth size="small"
                    InputProps={{ sx: { borderRadius: 2 } }} />
                </Box>
              </>
            )}

            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={loading}
              size="large"
              sx={{
                py: 1.5, borderRadius: 2.5, fontSize: 16, fontWeight: 700,
                background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                boxShadow: '0 8px 24px rgba(26,35,126,0.35)',
                '&:hover': { boxShadow: '0 12px 32px rgba(26,35,126,0.45)' },
              }}
            >
              {loading ? <CircularProgress size={24} sx={{ color: '#fff' }} /> : mode === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </form>

          {/* Demo credentials */}
          {mode === 'login' && (
            <Accordion disableGutters elevation={0} sx={{
              mt: 2, borderRadius: '12px !important', overflow: 'hidden',
              border: '1px solid #e8eaf6', bgcolor: '#f8f9ff',
              '&::before': { display: 'none' },
            }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#1a237e' }} />}
                sx={{ minHeight: 40, '& .MuiAccordionSummary-content': { my: 0.5 } }}>
                <Typography variant="caption" fontWeight={700} sx={{ color: '#1a237e', fontSize: 11 }}>
                  Demo Accounts
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0, pb: 1.5, px: 1.5 }}>
                {DEMO_ACCOUNTS.map((acc) => (
                  <Box key={acc.username} onClick={() => setForm({ ...form, username: acc.username, password: acc.password })}
                    sx={{
                      display: 'flex', alignItems: 'center', gap: 1, py: 0.6, px: 1,
                      borderRadius: 1.5, cursor: 'pointer', mb: 0.3,
                      '&:hover': { bgcolor: '#e8eaf6' }, transition: 'background 0.15s',
                    }}>
                    <Chip label={acc.role} size="small" sx={{
                      height: 20, fontSize: 9, fontWeight: 700, minWidth: 72,
                      bgcolor: `${acc.color}15`, color: acc.color,
                      border: `1px solid ${acc.color}30`,
                    }} />
                    <Typography variant="caption" fontWeight={600} sx={{ flex: 1, fontSize: 11 }}>
                      {acc.username}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: 10 }}>
                      {acc.spec || acc.password}
                    </Typography>
                  </Box>
                ))}
              </AccordionDetails>
            </Accordion>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
