import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableHead, TableBody, TableRow, TableCell,
  Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, CircularProgress, Alert, IconButton, Avatar,
  Switch, FormControlLabel, Tooltip,
} from '@mui/material';
import {
  Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon,
  Person as PersonIcon, CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
} from '@mui/icons-material';
import { getTechnicians, createTechnician, updateTechnician, deleteTechnician } from '../api';

const SPECIALIZATIONS = ['Electrical', 'Plumbing', 'Elevator', 'Security', 'Cleanliness', 'Carpentry'];

const emptyForm = {
  username: '', password: '', email: '', first_name: '', last_name: '',
  phone: '', specialization: '', block: '', is_available: true,
};

export default function Technicians() {
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTech, setEditingTech] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(null);

  const load = async () => {
    try {
      const res = await getTechnicians();
      setTechnicians(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const handleOpen = (tech = null) => {
    setError('');
    if (tech) {
      setEditingTech(tech);
      setForm({ ...emptyForm, ...tech, password: '' });
    } else {
      setEditingTech(null);
      setForm(emptyForm);
    }
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    setError('');
    try {
      if (editingTech) {
        const { password, username, ...updateData } = form;
        await updateTechnician(editingTech.id, updateData);
        setSuccess('Technician updated successfully');
      } else {
        if (!form.username || !form.password) {
          setError('Username and password are required');
          return;
        }
        await createTechnician(form);
        setSuccess('Technician added successfully');
      }
      setOpenDialog(false);
      load();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(JSON.stringify(err.response?.data) || 'Failed');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteTechnician(id);
      setConfirmDelete(null);
      setSuccess('Technician removed');
      load();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) { setError('Failed to remove technician'); }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} sx={{
            background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Technicians
          </Typography>
          <Typography variant="body2" color="text.secondary">Manage your maintenance workforce</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpen()} sx={{
          borderRadius: 3, textTransform: 'none', fontWeight: 600, px: 3,
          background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          boxShadow: '0 4px 14px rgba(26,35,126,0.3)',
          '&:hover': { boxShadow: '0 6px 20px rgba(26,35,126,0.4)' },
        }}>
          Add Technician
        </Button>
      </Box>

      {success && <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>{success}</Alert>}

      <Paper sx={{ borderRadius: 3, overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ background: 'linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%)' }}>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Technician</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Contact</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Specialization</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Active Tasks</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Resolved</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {technicians.length === 0 ? (
              <TableRow><TableCell colSpan={7} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                No technicians added yet. Click "Add Technician" to get started.
              </TableCell></TableRow>
            ) : (
              technicians.map((t) => (
                <TableRow key={t.id} sx={{ '&:hover': { bgcolor: '#f8f9ff' }, transition: 'background 0.2s' }}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Avatar sx={{
                        width: 40, height: 40, fontSize: 16, fontWeight: 700,
                        background: 'linear-gradient(135deg, #1a237e 0%, #3949ab 100%)',
                      }}>
                        {(t.first_name?.[0] || t.username?.[0] || '?').toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {t.first_name} {t.last_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">@{t.username}</Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{t.email || '—'}</Typography>
                    <Typography variant="caption" color="text.secondary">{t.phone || ''}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={t.specialization || 'General'} size="small" sx={{
                      fontWeight: 600, borderRadius: 2,
                      background: 'linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%)',
                      color: '#1a237e',
                    }} />
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={t.is_available ? <ActiveIcon fontSize="small" /> : <InactiveIcon fontSize="small" />}
                      label={t.is_available ? 'Available' : 'Unavailable'}
                      size="small"
                      sx={{
                        fontWeight: 600, borderRadius: 2,
                        bgcolor: t.is_available ? '#e8f5e9' : '#ffebee',
                        color: t.is_available ? '#2e7d32' : '#c62828',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={t.active_tasks} size="small" sx={{
                      bgcolor: t.active_tasks > 0 ? '#fff3e0' : '#f5f5f5',
                      color: t.active_tasks > 0 ? '#e65100' : '#999',
                      fontWeight: 700, minWidth: 32,
                    }} />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} color="success.main">{t.resolved_tasks}</Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Edit"><IconButton size="small" onClick={() => handleOpen(t)} sx={{ color: '#1a237e' }}><EditIcon fontSize="small" /></IconButton></Tooltip>
                    <Tooltip title="Remove"><IconButton size="small" onClick={() => setConfirmDelete(t)} sx={{ color: '#c62828' }}><DeleteIcon fontSize="small" /></IconButton></Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>

      {/* Add / Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)', color: '#fff', fontWeight: 700,
        }}>
          {editingTech ? 'Edit Technician' : 'Add New Technician'}
        </DialogTitle>
        <DialogContent sx={{ pt: '24px !important' }}>
          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}
          {!editingTech && (
            <>
              <TextField label="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}
                fullWidth sx={{ mb: 2 }} size="small" required />
              <TextField label="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                fullWidth sx={{ mb: 2 }} size="small" required />
            </>
          )}
          <Box sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
            <TextField label="First Name" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })}
              fullWidth size="small" />
            <TextField label="Last Name" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })}
              fullWidth size="small" />
          </Box>
          <TextField label="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
            fullWidth sx={{ mb: 2 }} size="small" />
          <TextField label="Phone" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
            fullWidth sx={{ mb: 2 }} size="small" />
          <TextField label="Specialization" select value={form.specialization} onChange={e => setForm({ ...form, specialization: e.target.value })}
            fullWidth sx={{ mb: 2 }} size="small">
            {SPECIALIZATIONS.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
          </TextField>
          <TextField label="Block" value={form.block} onChange={e => setForm({ ...form, block: e.target.value })}
            fullWidth sx={{ mb: 2 }} size="small" />
          <FormControlLabel
            control={<Switch checked={form.is_available} onChange={e => setForm({ ...form, is_available: e.target.checked })} />}
            label="Available for assignments"
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenDialog(false)} sx={{ borderRadius: 2, textTransform: 'none' }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} sx={{
            borderRadius: 2, textTransform: 'none', fontWeight: 600,
            background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          }}>
            {editingTech ? 'Save Changes' : 'Add Technician'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!confirmDelete} onClose={() => setConfirmDelete(null)}
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>Remove Technician?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove <b>{confirmDelete?.first_name} {confirmDelete?.last_name}</b>?
            Any active tasks will be unassigned and set back to Open.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setConfirmDelete(null)} sx={{ borderRadius: 2, textTransform: 'none' }}>Cancel</Button>
          <Button variant="contained" color="error" onClick={() => handleDelete(confirmDelete.id)} sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600 }}>
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
