import { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableHead, TableBody, TableRow, TableCell,
  Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, CircularProgress, Alert, IconButton, Select,
  FormControl, InputLabel, Avatar,
} from '@mui/material';
import { Add as AddIcon, Visibility as ViewIcon, PersonAdd as AssignIcon } from '@mui/icons-material';
import { getComplaints, createComplaint, updateComplaint, predictCategory, getTechnicians, assignTechnician } from '../api';
import { useAuth } from '../AuthContext';

const STATUS_COLORS = {
  Open: { bg: '#e3f2fd', color: '#1565c0' },
  Assigned: { bg: '#fff3e0', color: '#e65100' },
  'In Progress': { bg: '#e8eaf6', color: '#283593' },
  Resolved: { bg: '#e8f5e9', color: '#2e7d32' },
  Closed: { bg: '#f5f5f5', color: '#616161' },
};

const PRIORITY_COLORS = {
  Low: { bg: '#e8f5e9', color: '#2e7d32' },
  Medium: { bg: '#e3f2fd', color: '#1565c0' },
  High: { bg: '#fff3e0', color: '#e65100' },
  Critical: { bg: '#fce4ec', color: '#c62828' },
};

const LOCATIONS = ['Block A', 'Block B', 'Block C', 'Clubhouse', 'Basement Parking', 'Main Gate'];

export default function Complaints() {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openNew, setOpenNew] = useState(false);
  const [openDetail, setOpenDetail] = useState(false);
  const [openAssign, setOpenAssign] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [newComplaint, setNewComplaint] = useState({ description: '', location: '' });
  const [aiPrediction, setAiPrediction] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [technicians, setTechnicians] = useState([]);
  const [selectedTech, setSelectedTech] = useState('');

  const loadComplaints = async () => {
    try {
      const params = {};
      if (filterStatus) params.status = filterStatus;
      if (filterCategory) params.category = filterCategory;
      const res = await getComplaints(params);
      setComplaints(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadComplaints(); }, [filterStatus, filterCategory]);

  const handleTextChange = async (text) => {
    setNewComplaint({ ...newComplaint, description: text });
    if (text.length > 15) {
      try {
        const res = await predictCategory(text);
        setAiPrediction(res.data);
      } catch (e) { /* ignore */ }
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    try {
      await createComplaint(newComplaint);
      setOpenNew(false);
      setNewComplaint({ description: '', location: '' });
      setAiPrediction(null);
      loadComplaints();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit complaint');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      await updateComplaint(id, { status: newStatus });
      loadComplaints();
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenAssign = async (complaint) => {
    setSelectedComplaint(complaint);
    setSelectedTech('');
    try {
      const res = await getTechnicians();
      setTechnicians(res.data);
    } catch (e) { console.error(e); }
    setOpenAssign(true);
  };

  const handleAssign = async () => {
    if (!selectedTech) return;
    try {
      await assignTechnician(selectedComplaint.id, selectedTech);
      setOpenAssign(false);
      loadComplaints();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <CircularProgress size={48} sx={{ color: '#1a237e' }} />
    </Box>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{
            background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Complaints
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {user?.role === 'admin' ? 'Manage and assign complaints' : 'Track your maintenance requests'}
          </Typography>
        </Box>
        {user?.role === 'resident' && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenNew(true)} sx={{
            borderRadius: 3, px: 3, fontWeight: 700,
            background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
            boxShadow: '0 4px 14px rgba(26,35,126,0.3)',
            '&:hover': { boxShadow: '0 6px 20px rgba(26,35,126,0.4)' },
          }}>
            New Complaint
          </Button>
        )}
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Status</InputLabel>
          <Select value={filterStatus} label="Status" onChange={(e) => setFilterStatus(e.target.value)}
            sx={{ borderRadius: 2.5 }}>
            <MenuItem value="">All</MenuItem>
            {['Open', 'Assigned', 'In Progress', 'Resolved', 'Closed'].map(s => (
              <MenuItem key={s} value={s}>{s}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Category</InputLabel>
          <Select value={filterCategory} label="Category" onChange={(e) => setFilterCategory(e.target.value)}
            sx={{ borderRadius: 2.5 }}>
            <MenuItem value="">All</MenuItem>
            {['Electrical', 'Plumbing', 'Elevator', 'Security', 'Cleanliness', 'Carpentry'].map(c => (
              <MenuItem key={c} value={c}>{c}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Complaints Table */}
      <Paper sx={{ borderRadius: 4, overflow: 'hidden' }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ background: 'linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%)' }}>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e', py: 2 }}>ID</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Location</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Category</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Priority</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Assigned To</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1a237e' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {complaints.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                  No complaints found
                </TableCell>
              </TableRow>
            ) : (
              complaints.map((c) => {
                const sc = STATUS_COLORS[c.status] || { bg: '#f5f5f5', color: '#666' };
                const pc = PRIORITY_COLORS[c.priority] || { bg: '#f5f5f5', color: '#666' };
                return (
                  <TableRow key={c.id} sx={{
                    '&:hover': { bgcolor: '#f8f9ff' },
                    transition: 'background 0.2s',
                  }}>
                    <TableCell>
                      <Typography variant="body2" fontWeight={700} color="#1a237e">#{c.id}</Typography>
                    </TableCell>
                    <TableCell sx={{ maxWidth: 280 }}>
                      <Typography variant="body2" noWrap fontWeight={500}>{c.description}</Typography>
                      {c.is_duplicate && (
                        <Chip label="Duplicate" size="small" sx={{
                          mt: 0.5, height: 20, fontSize: 10, fontWeight: 700,
                          bgcolor: '#fff3e0', color: '#e65100',
                        }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{c.location}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={c.category} size="small" sx={{
                        fontWeight: 600, borderRadius: 2,
                        bgcolor: '#e8eaf6', color: '#1a237e',
                      }} />
                    </TableCell>
                    <TableCell>
                      <Chip label={c.priority} size="small" sx={{
                        fontWeight: 700, borderRadius: 2,
                        bgcolor: pc.bg, color: pc.color,
                      }} />
                    </TableCell>
                    <TableCell>
                      <Chip label={c.status} size="small" variant="outlined" sx={{
                        fontWeight: 700, borderRadius: 2,
                        bgcolor: sc.bg, color: sc.color, borderColor: sc.color,
                      }} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {c.assigned_staff_name || <span style={{ color: '#999' }}>Unassigned</span>}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                        <IconButton size="small" onClick={() => { setSelectedComplaint(c); setOpenDetail(true); }} sx={{ color: '#1a237e' }}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
                        {user?.role === 'admin' && (c.status === 'Open' || !c.assigned_staff) && (
                          <Button size="small" startIcon={<AssignIcon />}
                            onClick={() => handleOpenAssign(c)}
                            sx={{
                              borderRadius: 2, fontSize: 11, fontWeight: 700,
                              color: '#1a237e', bgcolor: '#e8eaf6',
                              '&:hover': { bgcolor: '#c5cae9' },
                            }}>
                            Assign
                          </Button>
                        )}
                        {user?.role === 'technician' && c.status === 'Assigned' && (
                          <Button size="small" onClick={() => handleStatusUpdate(c.id, 'In Progress')}
                            sx={{ borderRadius: 2, fontSize: 11, fontWeight: 700, color: '#283593', bgcolor: '#e8eaf6' }}>
                            Start
                          </Button>
                        )}
                        {user?.role === 'technician' && c.status === 'In Progress' && (
                          <Button size="small" onClick={() => handleStatusUpdate(c.id, 'Resolved')}
                            sx={{ borderRadius: 2, fontSize: 11, fontWeight: 700, color: '#2e7d32', bgcolor: '#e8f5e9' }}>
                            Resolve
                          </Button>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Paper>

      {/* New Complaint Dialog */}
      <Dialog open={openNew} onClose={() => setOpenNew(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          color: '#fff', fontWeight: 700,
        }}>Submit New Complaint</DialogTitle>
        <DialogContent sx={{ pt: '24px !important' }}>
          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}
          <TextField
            label="Describe your issue"
            multiline rows={4} fullWidth sx={{ mb: 2 }}
            value={newComplaint.description}
            onChange={(e) => handleTextChange(e.target.value)}
            InputProps={{ sx: { borderRadius: 2 } }}
          />
          {aiPrediction && (
            <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }} icon={false}>
              <Typography variant="body2" fontWeight={700} sx={{ mb: 0.5 }}>AI Prediction</Typography>
              <Typography variant="body2">
                Category: <b>{aiPrediction.category}</b> &bull; Priority: <b>{aiPrediction.priority}</b>
              </Typography>
            </Alert>
          )}
          <TextField
            label="Location" select fullWidth sx={{ mb: 1 }}
            value={newComplaint.location}
            onChange={(e) => setNewComplaint({ ...newComplaint, location: e.target.value })}
            InputProps={{ sx: { borderRadius: 2 } }}
          >
            {LOCATIONS.map(l => <MenuItem key={l} value={l}>{l}</MenuItem>)}
          </TextField>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenNew(false)} sx={{ borderRadius: 2 }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}
            disabled={submitting || !newComplaint.description || !newComplaint.location}
            sx={{
              borderRadius: 2, fontWeight: 700,
              background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
            }}>
            {submitting ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={openDetail} onClose={() => setOpenDetail(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          color: '#fff', fontWeight: 700,
        }}>
          Complaint #{selectedComplaint?.id}
        </DialogTitle>
        <DialogContent sx={{ pt: '24px !important' }}>
          {selectedComplaint && (
            <Box>
              <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>{selectedComplaint.description}</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, mb: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Location</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedComplaint.location}</Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedComplaint.category}</Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Priority</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedComplaint.priority}</Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedComplaint.status}</Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Assigned To</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedComplaint.assigned_staff_name || 'Unassigned'}</Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8f9ff' }}>
                  <Typography variant="caption" color="text.secondary">Created</Typography>
                  <Typography variant="body2" fontWeight={600}>{new Date(selectedComplaint.created_at).toLocaleString()}</Typography>
                </Box>
              </Box>
              {selectedComplaint.ai_explanation && (
                <Alert severity="info" sx={{ borderRadius: 2, mb: 1 }} icon={false}>
                  <Typography variant="body2" fontWeight={700} sx={{ mb: 0.5 }}>AI Analysis</Typography>
                  <Typography variant="body2">{selectedComplaint.ai_explanation}</Typography>
                </Alert>
              )}
              {selectedComplaint.is_duplicate && (
                <Alert severity="warning" sx={{ borderRadius: 2 }}>
                  Duplicate of Complaint #{selectedComplaint.master_complaint} (Similarity: {(selectedComplaint.similarity_score * 100).toFixed(1)}%)
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          {user?.role === 'admin' && selectedComplaint && (selectedComplaint.status === 'Open' || !selectedComplaint.assigned_staff) && (
            <Button variant="contained" startIcon={<AssignIcon />}
              onClick={() => { setOpenDetail(false); handleOpenAssign(selectedComplaint); }}
              sx={{
                borderRadius: 2, fontWeight: 700, mr: 'auto',
                background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
              }}>
              Assign Technician
            </Button>
          )}
          <Button onClick={() => setOpenDetail(false)} sx={{ borderRadius: 2 }}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Assign Technician Dialog */}
      <Dialog open={openAssign} onClose={() => setOpenAssign(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          color: '#fff', fontWeight: 700,
        }}>
          Assign Technician
        </DialogTitle>
        <DialogContent sx={{ pt: '24px !important' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Complaint #{selectedComplaint?.id}: {selectedComplaint?.category} at {selectedComplaint?.location}
          </Typography>
          <FormControl fullWidth size="small">
            <InputLabel>Select Technician</InputLabel>
            <Select value={selectedTech} label="Select Technician" onChange={e => setSelectedTech(e.target.value)}
              sx={{ borderRadius: 2 }}>
              {technicians.map(t => (
                <MenuItem key={t.id} value={t.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Avatar sx={{ width: 28, height: 28, fontSize: 12, bgcolor: '#1a237e' }}>
                      {(t.first_name?.[0] || '?').toUpperCase()}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{t.first_name} {t.last_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {t.specialization || 'General'} &bull; {t.active_tasks} active tasks
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenAssign(false)} sx={{ borderRadius: 2 }}>Cancel</Button>
          <Button variant="contained" onClick={handleAssign} disabled={!selectedTech} sx={{
            borderRadius: 2, fontWeight: 700,
            background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
          }}>
            Assign
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
